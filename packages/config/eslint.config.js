import js from "@eslint/js";
import nextPlugin from "@next/eslint-plugin-next";
import globals from "globals";
import jsxA11y from "eslint-plugin-jsx-a11y";
import reactPlugin from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

const sharedRules = {
  ...reactHooks.configs.recommended.rules,
  "react/react-in-jsx-scope": "off",
  "react/prop-types": "off",
  "@next/next/no-html-link-for-pages": "off",
};

export default [
  {
    ignores: [
      "**/.next/**",
      "**/.turbo/**",
      "**/.vercel/**",
      "**/dist/**",
      "**/coverage/**",
      "**/node_modules/**",
      "**/next-env.d.ts",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{js,mjs,cjs,ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    plugins: {
      react: reactPlugin,
      "react-hooks": reactHooks,
      "jsx-a11y": jsxA11y,
      "@next/next": nextPlugin,
    },
    rules: sharedRules,
    settings: {
      react: {
        version: "detect",
      },
    },
  },
];
