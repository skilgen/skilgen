from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text()


class UpgradeFlowTests(unittest.TestCase):
    def test_pricing_cards_render_expected_plans(self) -> None:
        source = read("apps/dashboard/app/dashboard/upgrade/page.tsx")

        self.assertIn('name: "Free"', source)
        self.assertIn('name: "Team"', source)
        self.assertIn('name: "Business"', source)
        self.assertIn('name: "Enterprise"', source)
        self.assertIn("PR comment engine", source)
        self.assertIn("bg-[#C9973A]", source)

    def test_free_plan_cta_is_disabled(self) -> None:
        source = read("apps/dashboard/app/dashboard/upgrade/page.tsx")

        self.assertIn("Current plan", source)
        self.assertIn("disabled", source)
        self.assertIn("cursor-not-allowed", source)

    def test_upgrade_button_has_seat_count_input(self) -> None:
        source = read("apps/dashboard/src/components/upgrade-button.tsx")

        self.assertIn("Seats", source)
        self.assertIn('type="number"', source)
        self.assertIn("value={seatCount}", source)
        self.assertIn("createCheckoutSession(plan, seatCount, accessToken)", source)
        self.assertIn("checkout_started", source)

    def test_posthog_is_initialized_from_layout_in_production_only(self) -> None:
        layout = read("apps/dashboard/app/layout.tsx")
        helper = read("apps/dashboard/src/lib/posthog.ts")
        upgrade = read("apps/dashboard/app/dashboard/upgrade/page.tsx")
        tracker = read("apps/dashboard/src/components/upgrade-page-tracker.tsx")

        self.assertIn("PostHogProvider", layout)
        self.assertIn('process.env.NODE_ENV !== "production"', helper)
        self.assertIn("posthog.init", helper)
        self.assertIn("UpgradePageTracker", upgrade)
        self.assertIn("upgrade_page_viewed", tracker)

    def test_checkout_helper_posts_authenticated_session_request(self) -> None:
        source = read("apps/dashboard/lib/stripe.ts")

        self.assertIn("/stripe/create-checkout-session", source)
        self.assertIn('Authorization: `Bearer ${accessToken}`', source)
        self.assertIn("seat_count: seatCount", source)
        self.assertIn("checkout_url", source)

    def test_billing_settings_fetches_subscription_and_shows_success(self) -> None:
        source = read("apps/dashboard/app/dashboard/settings/billing/page.tsx")
        button_source = read("apps/dashboard/app/dashboard/settings/billing/manage-billing-button.tsx")

        self.assertIn("/stripe/subscription", source)
        self.assertIn("Your plan has been upgraded.", source)
        self.assertIn("Current plan", source)
        self.assertIn("Manage billing", button_source)
        self.assertIn("Upgrade plan", source)
