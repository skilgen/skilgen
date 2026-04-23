"use client";

import type { ErrorInfo, ReactElement, ReactNode } from "react";
import { Component } from "react";

import { SectionFallback } from "./section-fallback";

type SectionErrorBoundaryProps = {
  children: ReactNode;
  section: string;
};

type SectionErrorBoundaryState = {
  hasError: boolean;
};

/** Catches client-side render failures inside a dashboard section. */
export class SectionErrorBoundary extends Component<SectionErrorBoundaryProps, SectionErrorBoundaryState> {
  state: SectionErrorBoundaryState = {
    hasError: false,
  };

  static getDerivedStateFromError(): SectionErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error(
      JSON.stringify({
        scope: "dashboard.section",
        event: "render_error",
        section: this.props.section,
        message: error.message,
        componentStack: info.componentStack,
      }),
    );
  }

  componentDidUpdate(previousProps: SectionErrorBoundaryProps): void {
    if (previousProps.section !== this.props.section && this.state.hasError) {
      this.setState({ hasError: false });
    }
  }

  render(): ReactElement {
    if (this.state.hasError) {
      return <SectionFallback section={this.props.section} />;
    }

    return <>{this.props.children}</>;
  }
}
