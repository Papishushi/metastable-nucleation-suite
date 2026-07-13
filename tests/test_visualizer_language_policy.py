from scripts.check_visualizer_language_policy import find_violations


def test_policy_rejects_javascript_and_typescript_application_code():
    assert find_violations(
        [
            "visualizer/src/app.js",
            "visualizer/src/app.mjs",
            "visualizer/src/app.cjs",
            "visualizer/src/app.ts",
            "visualizer/src/app.tsx",
        ]
    ) == [
        "visualizer/src/app.cjs",
        "visualizer/src/app.js",
        "visualizer/src/app.mjs",
        "visualizer/src/app.ts",
        "visualizer/src/app.tsx",
    ]


def test_policy_allows_only_the_documented_generated_wasm_bindings():
    assert find_violations(
        [
            "visualizer/generated/metastable_visualizer.js",
            "visualizer/generated/metastable_visualizer.d.ts",
            "visualizer/generated/other.js",
        ]
    ) == ["visualizer/generated/other.js"]
