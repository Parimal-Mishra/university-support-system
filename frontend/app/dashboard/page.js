"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { chatWithAssistant } from "../../lib/api";

export default function Dashboard() {
  const router = useRouter();
  const messagesEndRef = useRef(null);

  const [user, setUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const storedUser = localStorage.getItem("user");

    if (!token || !storedUser) {
      router.replace("/");
      return;
    }

    try {
      setUser(JSON.parse(storedUser));
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      router.replace("/");
    }
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery || loading) {
      return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
      router.replace("/");
      return;
    }

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: trimmedQuery,
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuery("");
    setLoading(true);

    try {
      const response = await chatWithAssistant(trimmedQuery, token);

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          response.answer ||
          response.message ||
          "I could not generate an answer.",
        sources: response.sources || [],
        grounding: response.grounding || null,
      };

      setMessages((previous) => [...previous, assistantMessage]);
    } catch (error) {
      if (
        error.message?.toLowerCase().includes("401") ||
        error.message?.toLowerCase().includes("authentication")
      ) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        router.replace("/");
        return;
      }

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: "assistant",
          content:
            error.message ||
            "Something went wrong while contacting the AI assistant.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    router.replace("/");
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-bold">
              ABES AI Support
            </h1>

            <p className="text-xs text-slate-400">
              University Student Support System
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-medium">
                {user?.full_name}
              </p>

              <p className="text-xs text-slate-500">
                {user?.role}
              </p>
            </div>

            <button
              onClick={handleLogout}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-red-500 hover:text-red-400"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main */}
      <div className="mx-auto flex min-h-[calc(100vh-73px)] max-w-6xl flex-col px-4 py-6 sm:px-6">
        {/* Welcome */}
        {messages.length === 0 && (
          <section className="flex flex-1 flex-col items-center justify-center py-12 text-center">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600/20 text-3xl">
              🤖
            </div>

            <h2 className="text-3xl font-bold">
              How can I help you?
            </h2>

            <p className="mt-3 max-w-xl text-slate-400">
              Ask questions about ABES academics, examinations,
              fees, policies, faculty, student services, and
              other university information.
            </p>

            <div className="mt-8 grid w-full max-w-3xl gap-3 sm:grid-cols-2">
              {[
                "What is the academic calendar for 2026–27?",
                "Where can I find my teacher's cabin?",
                "What are the examination rules?",
                "What student services are available?",
              ].map((question) => (
                <button
                  key={question}
                  onClick={() => setQuery(question)}
                  className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-left text-sm text-slate-300 transition hover:border-blue-500 hover:bg-slate-900/80"
                >
                  {question}
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Messages */}
        {messages.length > 0 && (
          <section className="flex-1 space-y-6 overflow-y-auto pb-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-3xl rounded-2xl px-5 py-4 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : message.error
                      ? "border border-red-900 bg-red-950/40 text-red-300"
                      : "border border-slate-800 bg-slate-900 text-slate-200"
                  }`}
                >
                  <p className="whitespace-pre-wrap text-sm leading-7">
                    {message.content}
                  </p>

                  {/* Sources */}
                  {message.role === "assistant" &&
                    message.sources?.length > 0 && (
                      <div className="mt-5 border-t border-slate-800 pt-4">
                        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                          Sources
                        </p>

                        <div className="space-y-2">
                          {message.sources.map((source, index) => (
                            <div
                              key={
                                source.chunk_id ||
                                source.document_id ||
                                index
                              }
                              className="rounded-lg bg-slate-950 px-3 py-2"
                            >
                              <p className="text-xs font-medium text-slate-300">
                                {source.document_name ||
                                  source.document_title ||
                                  source.document_id ||
                                  `Source ${index + 1}`}
                              </p>

                              {source.score !== undefined && (
                                <p className="mt-1 text-xs text-slate-600">
                                  Retrieval score:{" "}
                                  {Number(source.score).toFixed(3)}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                  {/* Grounding */}
                  {message.role === "assistant" &&
                    message.grounding && (
                      <div className="mt-4 text-xs text-slate-500">
                        Grounding:{" "}
                        <span className="text-slate-400">
                          {message.grounding.decision ||
                            message.grounding.status ||
                            "Validated"}
                        </span>
                      </div>
                    )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl border border-slate-800 bg-slate-900 px-5 py-4">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-500" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-500 [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-500 [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </section>
        )}

        {/* Input */}
        <section className="sticky bottom-0 bg-slate-950 pt-4">
          <form
            onSubmit={handleSubmit}
            className="mx-auto max-w-4xl"
          >
            <div className="flex items-end gap-3 rounded-2xl border border-slate-700 bg-slate-900 p-3 shadow-xl">
              <textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey
                  ) {
                    event.preventDefault();
                    event.currentTarget.form?.requestSubmit();
                  }
                }}
                rows={1}
                placeholder="Ask anything about ABES..."
                disabled={loading}
                className="max-h-32 min-h-12 flex-1 resize-none bg-transparent px-3 py-3 text-sm text-white outline-none placeholder:text-slate-500 disabled:opacity-50"
              />

              <button
                type="submit"
                disabled={!query.trim() || loading}
                className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? "..." : "Ask"}
              </button>
            </div>

            <p className="mt-2 text-center text-xs text-slate-600">
              Answers are generated from the university knowledge base.
            </p>
          </form>
        </section>
      </div>
    </main>
  );
}