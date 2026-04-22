export async function createPortalSession(accessToken: string): Promise<string> {
  const API = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
  const res = await fetch(`${API}/stripe/create-portal-session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      return_url: `${window.location.origin}/dashboard/settings/billing`,
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `API error ${res.status}`);
  }
  return data.portal_url;
}
