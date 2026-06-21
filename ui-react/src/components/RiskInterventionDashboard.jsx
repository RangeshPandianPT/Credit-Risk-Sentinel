import React, { useEffect, useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const FALLBACK_CUSTOMERS = [
  {
    id: 100045,
    name: "Alicia W.",
    riskScore: 82,
    stressFactor: "salary_delay",
    reasons: ["Salary drift", "Late payment trend", "Rising DPD"],
    trend: [
      { month: "Sep", stress: 38 },
      { month: "Oct", stress: 42 },
      { month: "Nov", stress: 50 },
      { month: "Dec", stress: 58 },
      { month: "Jan", stress: 64 },
      { month: "Feb", stress: 72 },
    ],
  },
  {
    id: 100112,
    name: "Jordan K.",
    riskScore: 76,
    stressFactor: "utilization_spike",
    reasons: ["Utilization spike", "High balance variance", "Cash advance uptick"],
    trend: [
      { month: "Sep", stress: 30 },
      { month: "Oct", stress: 36 },
      { month: "Nov", stress: 44 },
      { month: "Dec", stress: 53 },
      { month: "Jan", stress: 57 },
      { month: "Feb", stress: 61 },
    ],
  },
  {
    id: 100231,
    name: "Priya S.",
    riskScore: 69,
    stressFactor: "payment_irregularity",
    reasons: ["Payment inconsistency", "Recent DPD", "Short-term volatility"],
    trend: [
      { month: "Sep", stress: 22 },
      { month: "Oct", stress: 24 },
      { month: "Nov", stress: 31 },
      { month: "Dec", stress: 40 },
      { month: "Jan", stress: 46 },
      { month: "Feb", stress: 52 },
    ],
  },
];

const STRESS_LABELS = {
  salary_delay: "Salary drift detected",
  utilization_spike: "Utilization spike",
  payment_irregularity: "Payment irregularity",
};

const TEMPLATE_LIBRARY = {
  salary_delay: {
    title: "Offer a payment holiday",
    message:
      "Hi {name}, we noticed a change in your salary timing. If it helps, we can offer a short payment holiday or a revised due date. Reply YES to explore options.",
  },
  utilization_spike: {
    title: "Spending support plan",
    message:
      "Hi {name}, it looks like your card usage has risen recently. We can help with a flexible payment plan or budgeting tips. Reply YES for support.",
  },
  payment_irregularity: {
    title: "Gentle nudge + tips",
    message:
      "Hi {name}, if recent payments feel hard to keep up with, we have simple tips and flexible options. Reply YES for a quick overview.",
  },
};

const riskTone = (score) => {
  if (score >= 85) return "bg-rose-500 text-white";
  if (score >= 70) return "bg-amber-400 text-slate-900";
  return "bg-emerald-400 text-slate-900";
};

const formatTemplate = (template, name) =>
  template.replaceAll("{name}", name);

export default function RiskInterventionDashboard() {
  const [customers, setCustomers] = useState(FALLBACK_CUSTOMERS);
  const [selected, setSelected] = useState(FALLBACK_CUSTOMERS[0]);
  const [outreach, setOutreach] = useState("ready");
  const [scoreInfo, setScoreInfo] = useState({});
  const [scoreState, setScoreState] = useState({ status: "idle", error: null });
  const [notifyStatus, setNotifyStatus] = useState("unknown");
  const [customerState, setCustomerState] = useState({
    status: "idle",
    error: null,
  });

  const suggestion = useMemo(() => {
    return TEMPLATE_LIBRARY[selected.stressFactor];
  }, [selected]);

  const activeScore = scoreInfo[selected.id]?.riskScore ?? selected.riskScore;
  const activeReasons = scoreInfo[selected.id]?.reasons ?? selected.reasons;
  const activeLatency = scoreInfo[selected.id]?.featureLatencyMs ?? null;
  const latencyOk = scoreInfo[selected.id]?.latencyOk ?? null;

  useEffect(() => {
    let isMounted = true;

    const fetchCustomers = async () => {
      setCustomerState({ status: "loading", error: null });
      try {
        const response = await fetch("/customers/high-risk");
        if (!response.ok) {
          throw new Error(`Customer list request failed (${response.status})`);
        }
        const data = await response.json();
        if (!isMounted) return;
        if (Array.isArray(data) && data.length > 0) {
          setCustomers(data);
          setSelected(data[0]);
        }
        setCustomerState({ status: "loaded", error: null });
      } catch (error) {
        if (!isMounted) return;
        setCustomers(FALLBACK_CUSTOMERS);
        setSelected(FALLBACK_CUSTOMERS[0]);
        setCustomerState({ status: "error", error: error.message });
      }
    };

    fetchCustomers();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    const fetchScore = async () => {
      setScoreState({ status: "loading", error: null });
      try {
        const response = await fetch("/score", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ customer_id: selected.id }),
        });

        if (!response.ok) {
          throw new Error(`Score request failed (${response.status})`);
        }

        const data = await response.json();
        if (!isMounted) return;

        setScoreInfo((prev) => ({
          ...prev,
          [selected.id]: {
            riskScore: data.risk_score,
            reasons: Array.isArray(data.reasons)
              ? data.reasons.map((item) => item.feature)
              : selected.reasons,
            featureLatencyMs: data.feature_latency_ms,
            latencyOk: data.latency_sla_ok,
          },
        }));
        setScoreState({ status: "loaded", error: null });
      } catch (error) {
        if (!isMounted) return;
        setScoreState({ status: "error", error: error.message });
      }
    };

    fetchScore();

    return () => {
      isMounted = false;
    };
  }, [selected]);

  const sendIntervention = async () => {
    setOutreach("sending");
    setNotifyStatus("unknown");
    const payload = {
      customerId: selected.id,
      channel: "sms_email",
      templateTitle: suggestion.title,
      message: formatTemplate(suggestion.message, selected.name),
      stressFactor: selected.stressFactor,
      riskScore: activeScore,
      reasons: activeReasons,
    };

    try {
      const response = await fetch("/api/notify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      setNotifyStatus(data.status || "unknown");
      setOutreach("sent");
    } catch (error) {
      setNotifyStatus("failed");
      setOutreach("error");
    }
  };

  return (
    <section
      className="min-h-screen w-full bg-slate-950 text-slate-100"
      style={{
        backgroundImage:
          "radial-gradient(circle at 10% 20%, rgba(16, 185, 129, 0.15), transparent 40%), radial-gradient(circle at 85% 15%, rgba(244, 114, 182, 0.2), transparent 45%), radial-gradient(circle at 50% 80%, rgba(56, 189, 248, 0.2), transparent 45%)",
      }}
    >
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10">
        <header className="flex flex-col gap-3">
          <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">
            Pre-Delinquency Command Center
          </p>
          <h1 className="text-4xl font-semibold text-slate-50">
            Risk Intervention Dashboard
          </h1>
          <p className="max-w-2xl text-sm text-slate-300">
            Identify orange accounts early and respond with flexible, empathetic
            interventions before they turn red.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5 shadow-lg shadow-emerald-500/10">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">High-risk customers</h2>
              {customerState.status === "loading" ? (
                <span className="text-xs text-slate-400">Loading list...</span>
              ) : customerState.status === "error" ? (
                <span className="text-xs text-rose-300">
                  List failed, showing fallback
                </span>
              ) : (
                <span className="text-xs text-slate-400">Last 24h signals</span>
              )}
            </div>

            <div className="mt-4 flex flex-col gap-3">
              {customers.map((customer) => (
                <button
                  key={customer.id}
                  onClick={() => setSelected(customer)}
                  className={`flex items-center justify-between rounded-xl border border-slate-800 px-4 py-3 text-left transition hover:border-emerald-400 ${
                    selected.id === customer.id
                      ? "bg-slate-900/80"
                      : "bg-slate-950/60"
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-semibold text-slate-100">
                      {customer.name}
                    </span>
                    <span className="text-xs text-slate-400">
                      {STRESS_LABELS[customer.stressFactor]}
                    </span>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${riskTone(
                      scoreInfo[customer.id]?.riskScore ?? customer.riskScore
                    )}`}
                  >
                    {scoreInfo[customer.id]?.riskScore ?? customer.riskScore}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5 shadow-lg shadow-sky-500/10">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-sky-300">
                  6-month stress trend
                </p>
                <h2 className="text-lg font-semibold text-slate-50">
                  {selected.name}
                </h2>
                <p className="text-xs text-slate-400">
                  {STRESS_LABELS[selected.stressFactor]}
                </p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${riskTone(
                  activeScore
                )}`}
              >
                Risk {activeScore}
              </span>
            </div>

            <div className="mt-4 h-48">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={selected.trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="month" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      border: "1px solid #1f2937",
                      color: "#e2e8f0",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="stress"
                    stroke="#38bdf8"
                    strokeWidth={3}
                    dot={{ r: 4, fill: "#38bdf8" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-5 rounded-xl border border-slate-800 bg-slate-900/70 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">
                Suggested intervention
              </p>
              <h3 className="mt-1 text-base font-semibold text-slate-50">
                {suggestion.title}
              </h3>
              <p className="mt-2 text-sm text-slate-300">
                {formatTemplate(suggestion.message, selected.name)}
              </p>

              <div className="mt-3 flex flex-wrap items-center gap-2">
                <span className="text-[11px] uppercase tracking-[0.2em] text-slate-400">
                  Health
                </span>
                <span
                  className={`rounded-full border px-2 py-1 text-[11px] font-semibold ${
                    latencyOk === null
                      ? "border-slate-700 text-slate-400"
                      : latencyOk
                        ? "border-emerald-500/40 text-emerald-300"
                        : "border-rose-500/40 text-rose-300"
                  }`}
                >
                  {activeLatency === null
                    ? "Latency unknown"
                    : `Latency ${activeLatency}ms`}
                </span>
                <span
                  className={`rounded-full border px-2 py-1 text-[11px] font-semibold ${
                    notifyStatus === "sent"
                      ? "border-emerald-500/40 text-emerald-300"
                      : notifyStatus === "failed"
                        ? "border-rose-500/40 text-rose-300"
                        : "border-slate-700 text-slate-400"
                  }`}
                >
                  SNS {notifyStatus}
                </span>
                {scoreState.status === "error" && (
                  <span className="text-[11px] text-rose-300">
                    Score fetch failed
                  </span>
                )}
              </div>

              <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-300">
                  Risk reasons
                </p>
                <ul className="mt-2 grid gap-2 text-xs text-slate-200">
                  {activeReasons.map((reason) => (
                    <li key={reason} className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 flex items-center gap-3">
                <button
                  onClick={sendIntervention}
                  className="rounded-full bg-emerald-400 px-4 py-2 text-xs font-semibold text-slate-950 transition hover:bg-emerald-300"
                >
                  Suggest Intervention
                </button>
                {outreach === "sending" && (
                  <span className="text-xs text-slate-400">
                    Sending empathetic outreach...
                  </span>
                )}
                {outreach === "sent" && (
                  <span className="text-xs text-emerald-300">
                    Outreach queued for delivery.
                  </span>
                )}
                {outreach === "error" && (
                  <span className="text-xs text-rose-300">
                    Could not send. Check SNS integration.
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
