import React, { useMemo, useState } from "react";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function getApiErrorMessage(payload) {
  if (!payload) return "Login failed. Please try again.";
  if (typeof payload === "string") return payload;
  return (
    payload.error ||
    payload.message ||
    payload.detail ||
    payload.msg ||
    "Login failed. Please try again."
  );
}

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);

  const [touched, setTouched] = useState({ email: false, password: false });
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState("");

  const errors = useMemo(() => {
    const next = {};
    const trimmedEmail = email.trim();

    if (!trimmedEmail) next.email = "Email is required.";
    else if (!EMAIL_REGEX.test(trimmedEmail)) next.email = "Enter a valid email address.";

    if (!password) next.password = "Password is required.";

    return next;
  }, [email, password]);

  const canSubmit = !submitting && Object.keys(errors).length === 0;

  async function onSubmit(e) {
    e.preventDefault();
    setApiError("");
    setTouched({ email: true, password: true });

    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const contentType = res.headers.get("content-type") || "";
      const data = contentType.includes("application/json") ? await res.json() : await res.text();

      if (!res.ok) {
        const message = getApiErrorMessage(data);
        setApiError(message);
        return;
      }

      const token =
        (data && (data.token || data.jwt || data.accessToken || data.access_token)) || "";

      if (!token) {
        setApiError("Login succeeded, but no token was returned by the API.");
        return;
      }

      const storage = rememberMe ? window.localStorage : window.sessionStorage;
      storage.setItem("token", token);

      window.location.assign("/dashboard");
    } catch (err) {
      setApiError(err?.message || "Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="min-h-screen flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-md">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 shadow-xl shadow-black/30 backdrop-blur">
            <div className="p-6 sm:p-8">
              <h1 className="text-2xl font-semibold tracking-tight">Sign in</h1>
              <p className="mt-1 text-sm text-slate-300">
                Enter your email and password to continue.
              </p>

              {apiError ? (
                <div
                  role="alert"
                  aria-live="polite"
                  className="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200"
                >
                  {apiError}
                </div>
              ) : null}

              <form onSubmit={onSubmit} className="mt-6 space-y-4" noValidate>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-slate-200">
                    Email
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    inputMode="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onBlur={() => setTouched((t) => ({ ...t, email: true }))}
                    disabled={submitting}
                    aria-invalid={touched.email && !!errors.email}
                    aria-describedby={touched.email && errors.email ? "email-error" : undefined}
                    className={[
                      "mt-1 w-full rounded-lg border bg-slate-950/40 px-3 py-2 text-slate-100 outline-none",
                      "placeholder:text-slate-500",
                      "focus:ring-2 focus:ring-sky-400/50 focus:border-sky-400/60",
                      touched.email && errors.email
                        ? "border-red-500/60 focus:ring-red-400/30 focus:border-red-400/60"
                        : "border-slate-800",
                      "disabled:opacity-60 disabled:cursor-not-allowed",
                    ].join(" ")}
                    placeholder="you@example.com"
                  />
                  {touched.email && errors.email ? (
                    <p id="email-error" className="mt-1 text-xs text-red-200">
                      {errors.email}
                    </p>
                  ) : null}
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-slate-200">
                    Password
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      onBlur={() => setTouched((t) => ({ ...t, password: true }))}
                      disabled={submitting}
                      aria-invalid={touched.password && !!errors.password}
                      aria-describedby={
                        touched.password && errors.password ? "password-error" : undefined
                      }
                      className={[
                        "w-full rounded-lg border bg-slate-950/40 px-3 py-2 pr-20 text-slate-100 outline-none",
                        "placeholder:text-slate-500",
                        "focus:ring-2 focus:ring-sky-400/50 focus:border-sky-400/60",
                        touched.password && errors.password
                          ? "border-red-500/60 focus:ring-red-400/30 focus:border-red-400/60"
                          : "border-slate-800",
                        "disabled:opacity-60 disabled:cursor-not-allowed",
                      ].join(" ")}
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((s) => !s)}
                      disabled={submitting}
                      className={[
                        "absolute inset-y-0 right-1 my-1 rounded-md px-3 text-xs font-medium",
                        "text-slate-200 hover:bg-slate-800/60 focus:outline-none focus:ring-2 focus:ring-sky-400/50",
                        "disabled:opacity-60 disabled:cursor-not-allowed",
                      ].join(" ")}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                  {touched.password && errors.password ? (
                    <p id="password-error" className="mt-1 text-xs text-red-200">
                      {errors.password}
                    </p>
                  ) : null}
                </div>

                <div className="flex items-center justify-between gap-3">
                  <label className="inline-flex items-center gap-2 text-sm text-slate-200">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      disabled={submitting}
                      className="h-4 w-4 rounded border-slate-700 bg-slate-950/40 text-sky-400 focus:ring-sky-400/50"
                    />
                    Remember me
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={!canSubmit}
                  className={[
                    "w-full rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-semibold text-slate-950",
                    "hover:bg-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-400/60 focus:ring-offset-2 focus:ring-offset-slate-950",
                    "disabled:opacity-60 disabled:cursor-not-allowed",
                    "flex items-center justify-center gap-2",
                  ].join(" ")}
                >
                  {submitting ? (
                    <>
                      <span
                        aria-hidden="true"
                        className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950/30 border-t-slate-950"
                      />
                      Logging in…
                    </>
                  ) : (
                    "Login"
                  )}
                </button>

                <p className="text-xs text-slate-400">
                  By continuing, you agree to the app’s terms and privacy policy.
                </p>
              </form>
            </div>
          </div>

          <p className="mt-6 text-center text-xs text-slate-500">
            Tip: use Tab to move between fields; errors are announced after submit.
          </p>
        </div>
      </div>
    </div>
  );
}

