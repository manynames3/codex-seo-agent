const ROUTES = {
  health: { path: "/health", methods: ["GET"] },
  reports: { path: "/api/reports", methods: ["GET"] },
  run: { path: "/api/run", methods: ["POST"] },
  connect: { path: "/auth/google/start", methods: ["GET"] },
};

export async function onRequest({ request, env, params }) {
  const routeName = normalizePathParam(params.path);
  const route = ROUTES[routeName];

  if (!route) {
    return json({ error: "Not found" }, 404);
  }

  if (!route.methods.includes(request.method)) {
    return json({ error: "Method not allowed" }, 405);
  }

  const backendUrl = String(env.BACKEND_URL || "").replace(/\/$/, "");
  const accessKey = String(env.BACKEND_ADMIN_TOKEN || "");

  if (!backendUrl || !accessKey) {
    return json({ error: "Service is not configured." }, 503);
  }

  if (routeName === "connect") {
    return startConnection(request, backendUrl, accessKey);
  }

  return proxyRequest(request, backendUrl, route.path, accessKey);
}

function normalizePathParam(path) {
  if (Array.isArray(path)) return path.join("/");
  return String(path || "");
}

async function startConnection(request, backendUrl, accessKey) {
  const incomingUrl = new URL(request.url);
  const siteUrl = incomingUrl.searchParams.get("site_url") || "";

  if (!siteUrl) {
    return json({ error: "Website is required." }, 400);
  }

  const upstreamUrl = new URL("/auth/google/start", backendUrl);
  upstreamUrl.searchParams.set("site_url", siteUrl);
  upstreamUrl.searchParams.set("token", accessKey);

  const upstream = await fetch(upstreamUrl, {
    headers: { accept: "text/html" },
    redirect: "manual",
  });

  const location = upstream.headers.get("location");
  if (location && upstream.status >= 300 && upstream.status < 400) {
    return Response.redirect(location, 302);
  }

  return copyResponse(upstream);
}

async function proxyRequest(request, backendUrl, path, accessKey) {
  const upstreamUrl = new URL(path, backendUrl);
  const init = {
    method: request.method,
    headers: {
      authorization: `Bearer ${accessKey}`,
      "content-type": request.headers.get("content-type") || "application/json",
    },
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
  }

  const upstream = await fetch(upstreamUrl, init);
  return copyResponse(upstream);
}

function copyResponse(response) {
  const headers = new Headers();
  const contentType = response.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  headers.set("cache-control", "no-store");
  return new Response(response.body, { status: response.status, headers });
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "cache-control": "no-store",
      "content-type": "application/json; charset=utf-8",
    },
  });
}
