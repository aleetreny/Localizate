import { rm } from "node:fs/promises"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { spawn } from "node:child_process"

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url))
const FRONT_ROOT = resolve(SCRIPT_DIR, "..")
const SHOULD_STRIP_EMBEDDED_DATA = Boolean((process.env.NEXT_PUBLIC_DATA_BASE_URL ?? "").trim())

await runNextBuild()

if (SHOULD_STRIP_EMBEDDED_DATA) {
  await rm(resolve(FRONT_ROOT, "out", "data"), { force: true, recursive: true })
}

async function runNextBuild() {
  const child = spawn("npm exec next build", {
    cwd: FRONT_ROOT,
    env: {
      ...process.env,
      STATIC_EXPORT: "1",
    },
    shell: true,
    stdio: "inherit",
  })

  const exitCode = await new Promise((resolveExitCode, reject) => {
    child.once("error", reject)
    child.once("exit", (code) => {
      resolveExitCode(code ?? 1)
    })
  })

  if (exitCode !== 0) {
    process.exit(exitCode)
  }
}
