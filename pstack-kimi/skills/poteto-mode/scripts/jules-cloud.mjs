#!/usr/bin/env node
// Jules REST API adapter for pstack cloud workers.
//
// Jules runs on a Google-hosted VM, works on a GitHub repository, and can open
// a pull request itself. This script is the only place pstack names the cloud
// provider. Skills call it; they never speak to the Jules API directly.
//
// Auth: JULES_API_KEY (https://jules.google.com/settings#api).
// Network: JULES_PROXY, else HTTPS_PROXY, else HTTP_PROXY, else direct.
//
// Exit codes: 0 ok, 1 failure, 2 usage, 3 needs a human, 4 timeout, 5 no PR.

import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

const API = "https://jules.googleapis.com/v1alpha";
const KEY = process.env.JULES_API_KEY || "";
const PROXY =
  process.env.JULES_PROXY ||
  process.env.HTTPS_PROXY ||
  process.env.HTTP_PROXY ||
  "";

const TERMINAL = new Set(["COMPLETED", "FAILED"]);
const WAITING = new Set(["AWAITING_PLAN_APPROVAL", "AWAITING_USER_FEEDBACK"]);

function fail(message, code = 1) {
  process.stderr.write(`jules-cloud: ${message}\n`);
  process.exit(code);
}

function usage() {
  process.stdout.write(`Usage:
  jules-cloud.mjs dispatch --repo <owner/name> --brief <file|-> [--branch main] [--title <text>] [--no-pr] [--json]
  jules-cloud.mjs status   --session <id> [--json]
  jules-cloud.mjs wait     --session <id> [--timeout 3600] [--interval 10] [--require-pr] [--json]
  jules-cloud.mjs send     --session <id> --brief <file|-> [--json]
  jules-cloud.mjs result   --session <id> [--timeout 600] [--idle 20] [--json]
  jules-cloud.mjs activities --session <id> [--limit 30] [--json]
  jules-cloud.mjs sources  [--json]

Environment:
  JULES_API_KEY   required; never pass the key on the command line
  JULES_PROXY     optional; defaults to HTTPS_PROXY, HTTP_PROXY, or direct

Exit codes: 0 ok, 1 failure, 2 usage, 3 needs a human, 4 timeout, 5 no PR.
`);
}

function parse(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (!a.startsWith("--")) {
      out._.push(a);
      continue;
    }
    const [k, inline] = a.slice(2).split("=", 2);
    if (k === "json" || k === "no-pr" || k === "require-pr") {
      out[k] = true;
      continue;
    }
    const v = inline !== undefined ? inline : argv[++i];
    if (v === undefined) fail(`--${k} needs a value`, 2);
    out[k] = v;
  }
  return out;
}

function request(path, { method = "GET", body } = {}) {
  const args = [
    "-sS",
    "--fail-with-body",
    "--max-time",
    "120",
    "-X",
    method,
    API + path,
    "-H",
    `x-goog-api-key: ${KEY}`,
    "-H",
    "Content-Type: application/json",
  ];
  if (PROXY) args.push("-x", PROXY);
  if (body !== undefined) args.push("--data-binary", JSON.stringify(body));

  let last;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const raw = execFileSync("curl", args, {
        encoding: "utf8",
        maxBuffer: 32 * 1024 * 1024,
      });
      return raw.trim() ? JSON.parse(raw) : {};
    } catch (error) {
      last = error;
      const text = `${error.stdout || ""}${error.stderr || ""}`.trim();
      const retryable = /HTTP 5\d\d|Could not resolve|timed out|EOF|SSL|connection (reset|refused)/i.test(
        text,
      );
      if (!retryable || attempt === 3) {
        fail(text || error.message);
      }
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 1000 * attempt);
    }
  }
  fail(last?.message || "request failed");
}

function sessionPath(id) {
  if (!id) fail("--session is required", 2);
  return `/sessions/${encodeURIComponent(id)}`;
}

function readBrief(source) {
  if (!source) fail("--brief is required", 2);
  let text;
  if (source === "-") {
    text = readFileSync(0, "utf8");
  } else {
    try {
      text = readFileSync(source, "utf8");
    } catch (error) {
      fail(`cannot read brief: ${error.message}`);
    }
  }
  text = text.trim();
  if (!text) fail("brief is empty", 2);
  return text;
}

function pullRequests(session) {
  return (session.outputs || [])
    .map((o) => o.pullRequest)
    .filter(Boolean)
    .map((pr) => ({ url: pr.url, title: pr.title, head: pr.headRef, base: pr.baseRef }));
}

function printSession(session, asJson) {
  const prs = pullRequests(session);
  if (asJson) {
    process.stdout.write(`${JSON.stringify({ ...session, pullRequests: prs }, null, 2)}\n`);
    return;
  }
  process.stdout.write(`session ${session.id}\n`);
  process.stdout.write(`state ${session.state || "STATE_UNSPECIFIED"}\n`);
  if (session.url) process.stdout.write(`url ${session.url}\n`);
  for (const pr of prs) process.stdout.write(`pr ${pr.url}\n`);
}

function cmdDispatch(args) {
  const repo = args.repo;
  if (!repo || !/^[^/\s]+\/[^/\s]+$/.test(repo)) {
    fail("--repo must be owner/name", 2);
  }
  const brief = readBrief(args.brief);
  const body = {
    prompt: brief,
    sourceContext: {
      source: `sources/github/${repo}`,
      githubRepoContext: { startingBranch: args.branch || "main" },
    },
    title: args.title || brief.split("\n")[0].slice(0, 80),
  };
  if (!args["no-pr"]) body.automationMode = "AUTO_CREATE_PR";
  const session = request("/sessions", { method: "POST", body });
  printSession(session, args.json);
}

function cmdStatus(args) {
  printSession(request(sessionPath(args.session)), args.json);
}

function cmdSend(args) {
  const brief = readBrief(args.brief);
  request(`${sessionPath(args.session)}:sendMessage`, {
    method: "POST",
    body: { prompt: brief },
  });
  printSession(request(sessionPath(args.session)), args.json);
}

function cmdResult(args) {
  const timeout = Number(args.timeout || 600);
  const idle = Number(args.idle || 20);
  const started = Date.now();
  let lastChange = Date.now();
  let lastKey = "";
  let message = "";
  for (;;) {
    const data = request(`${sessionPath(args.session)}/activities?pageSize=100`);
    const activities = data.activities || [];
    const newest = activities[activities.length - 1];
    if (newest?.name && newest.name !== lastKey) {
      lastKey = newest.name;
      lastChange = Date.now();
    }
    const messages = activities.filter((a) => a.agentMessaged?.agentMessage);
    if (messages.length) message = messages[messages.length - 1].agentMessaged.agentMessage;
    if (message && Date.now() - lastChange >= idle * 1000) break;
    if (Date.now() - started > timeout * 1000) {
      if (message) process.stdout.write(`${message}\n`);
      fail(`no stable agent message after ${timeout}s`, 4);
    }
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 5000);
  }
  if (args.json) {
    process.stdout.write(`${JSON.stringify({ session: args.session, message }, null, 2)}\n`);
  } else {
    process.stdout.write(`${message}\n`);
  }
}

function cmdActivities(args) {
  const limit = Number(args.limit || 30);
  const data = request(`${sessionPath(args.session)}/activities?pageSize=${limit}`);
  const activities = data.activities || [];
  if (args.json) {
    process.stdout.write(`${JSON.stringify(activities, null, 2)}\n`);
    return;
  }
  for (const a of activities) {
    const type =
      Object.keys(a).find((k) => k !== "name" && k !== "id" && k !== "createTime" && k !== "originator") ||
      "activity";
    const detail =
      a.progressUpdated?.title ||
      a.progressUpdated?.description ||
      a.agentMessaged?.agentMessage ||
      a.userMessaged?.userMessage ||
      a.planGenerated?.plan?.steps?.map((s) => s.title).join("; ") ||
      (a.sessionCompleted ? "session completed" : "") ||
      "";
    process.stdout.write(`${a.createTime || ""} ${a.originator || ""} ${type} ${String(detail).replace(/\s+/g, " ").slice(0, 240)}\n`);
  }
}

function cmdSources(args) {
  const data = request("/sources");
  if (args.json) {
    process.stdout.write(`${JSON.stringify(data, null, 2)}\n`);
    return;
  }
  for (const s of data.sources || []) process.stdout.write(`${s.name}\n`);
}

function cmdWait(args) {
  const timeout = Number(args.timeout || 3600);
  const interval = Number(args.interval || 10);
  const started = Date.now();
  let lastState = "";
  let session = {};
  for (;;) {
    session = request(sessionPath(args.session));
    const state = session.state || "STATE_UNSPECIFIED";
    if (state !== lastState) {
      process.stderr.write(`jules-cloud: ${args.session} ${state}\n`);
      lastState = state;
    }
    if (TERMINAL.has(state)) break;
    if (WAITING.has(state)) {
      printSession(session, args.json);
      fail(`${state}; resolve it in ${session.url || "the Jules web UI"}`, 3);
    }
    if (Date.now() - started > timeout * 1000) {
      printSession(session, args.json);
      fail(`timed out after ${timeout}s in ${state}`, 4);
    }
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, interval * 1000);
  }
  printSession(session, args.json);
  if (session.state === "FAILED") fail("session failed", 1);
  if (args["require-pr"] && pullRequests(session).length === 0) {
    fail("completed without a pull request", 5);
  }
}

const argv = process.argv.slice(2);
const cmd = argv[0];
if (!cmd || cmd === "-h" || cmd === "--help" || cmd === "help") {
  usage();
  process.exit(0);
}
if (!KEY) fail("JULES_API_KEY is not set", 2);

const args = parse(argv.slice(1));
const commands = {
  dispatch: cmdDispatch,
  status: cmdStatus,
  wait: cmdWait,
  send: cmdSend,
  result: cmdResult,
  activities: cmdActivities,
  sources: cmdSources,
};
if (!commands[cmd]) {
  usage();
  fail(`unknown command: ${cmd}`, 2);
}
commands[cmd](args);