/**
 * Starts a Stripe Checkout subscription flow for a paid Skillayer plan.
 */
export async function createCheckoutSession(
  plan: "team" | "business",
  seatCount: number,
  accessToken: string,
): Promise<string> {
  const API = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";
  const res = await fetch(`${API}/stripe/create-checkout-session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      plan,
      seat_count: seatCount,
      success_url: `${window.location.origin}/dashboard/settings/billing?success=true&plan=${plan}`,
      cancel_url: `${window.location.origin}/dashboard/upgrade`,
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `API error ${res.status}`);
  }
  return data.checkout_url;
}
