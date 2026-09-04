import { createHash } from "node:crypto";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const sourceRoot = process.cwd();
const targetRoot = process.argv[2] ? path.resolve(process.argv[2]) : null;

if (!targetRoot) {
  console.error("Usage: npm run verify:mirror -- /path/to/other/dashboard");
  process.exit(2);
}

const ignoredDirectories = new Set([
  ".git",
  ".next",
  ".sites-runtime",
  ".wrangler",
  "coverage",
  "dist",
  "node_modules",
  "out",
  "outputs",
  "work",
]);

const ignoredFiles = new Set([
  ".env.example",
  "next-env.d.ts",
  "next.config.mjs",
  "tsconfig.tsbuildinfo",
]);

async function inventory(root, relativeDirectory = "") {
  const directory = path.join(root, relativeDirectory);
  const entries = await readdir(directory, { withFileTypes: true });
  const files = new Map();

  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    if (entry.isDirectory() && ignoredDirectories.has(entry.name)) continue;
    if (entry.isFile() && ignoredFiles.has(entry.name)) continue;

    const relativePath = path.join(relativeDirectory, entry.name);
    if (entry.isDirectory()) {
      for (const [nestedPath, digest] of await inventory(root, relativePath)) {
        files.set(nestedPath, digest);
      }
      continue;
    }

    if (!entry.isFile()) continue;
    const content = await readFile(path.join(root, relativePath));
    files.set(
      relativePath.split(path.sep).join("/"),
      createHash("sha256").update(content).digest("hex"),
    );
  }

  return files;
}

const [sourceFiles, targetFiles] = await Promise.all([
  inventory(sourceRoot),
  inventory(targetRoot),
]);

const allPaths = [...new Set([...sourceFiles.keys(), ...targetFiles.keys()])].sort();
const differences = allPaths.filter(
  (relativePath) => sourceFiles.get(relativePath) !== targetFiles.get(relativePath),
);

if (differences.length > 0) {
  console.error("Sites/GitHub mirror mismatch:");
  for (const relativePath of differences) {
    const state = !sourceFiles.has(relativePath)
      ? "only in target"
      : !targetFiles.has(relativePath)
        ? "only in source"
        : "content differs";
    console.error(`- ${relativePath}: ${state}`);
  }
  process.exit(1);
}

console.log(`Mirror verified: ${sourceFiles.size} files are identical.`);
