import { SectionErrorBoundary } from "@/components/section-error-boundary";
import { StubPage } from "@/components/stub-page";

export default function SkillsPage() {
  return (
    <SectionErrorBoundary section="skills">
      <StubPage pageName="Skills" />
    </SectionErrorBoundary>
  );
}
