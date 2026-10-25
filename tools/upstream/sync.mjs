#!/usr/bin/env node
/**
 * Sync the upstream sources pinned in UPSTREAM.json into .upstream/ (gitignored).
 *
 *   node tools/upstream/sync.mjs          check out the pinned commit of every source
 *   node tools/upstream/sync.mjs --check  fetch, then report how far each pin is behind
 *
 * Writes only under .upstream/. Never touches tracked files, never moves a pin.
 * A moved or rewritten upstream history surfaces as "pin not found" instead of a
 * silent checkout of something else.
 */
import { existsSync, mkdirSync, readFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..')
const checkOnly = process.argv.includes('--check')

function run(args, cwd, { tolerate = false } = {}) {
  const result = spawnSync('git', args, { cwd, stdio: 'inherit' })
  if (result.error) throw new Error(`git ${args[0]} could not start: ${result.error.message}`)
  if (result.status !== 0 && !tolerate) {
    throw new Error(`git ${args.join(' ')} exited ${result.status}`)
  }
  return result.status
}

function ensureClone(source) {
  const dir = join(REPO_ROOT, source.checkout)
  if (!existsSync(join(dir, '.git'))) {
    mkdirSync(dirname(dir), { recursive: true })
    console.log(`   clone ${source.repo} -> ${source.checkout}`)
    run(['clone', '--filter=blob:none', '--no-checkout', source.repo, dir], REPO_ROOT)
  }
  if (source.sparse?.length) {
    console.log(`   sparse-checkout ${source.sparse.join(', ')}`)
    run(['sparse-checkout', 'init', '--cone'], dir, { tolerate: true })
    run(['sparse-checkout', 'set', ...source.sparse], dir)
  }
  console.log('   fetch origin')
  run(['fetch', '--filter=blob:none', '--tags', 'origin'], dir)
  return dir
}

function main() {
  const manifest = JSON.parse(readFileSync(join(REPO_ROOT, 'UPSTREAM.json'), 'utf8'))
  const sources = manifest.sources ?? {}
  const names = Object.keys(sources)
  if (names.length === 0) throw new Error('UPSTREAM.json has no sources')

  for (const name of names) {
    const source = sources[name]
    console.log(`\n== ${name}  ${source.version ?? '?'} @ ${String(source.commit).slice(0, 7)}`)
    const dir = ensureClone(source)

    if (checkOnly) {
      run(['remote', 'set-head', 'origin', '-a'], dir, { tolerate: true })
      console.log('   commits after the pin on origin/HEAD:')
      run(['rev-list', '--count', `${source.commit}..origin/HEAD`], dir, { tolerate: true })
      continue
    }

    console.log(`   checkout ${String(source.commit).slice(0, 7)}`)
    const status = run(['checkout', '--force', '--detach', source.commit], dir, { tolerate: true })
    if (status !== 0) {
      throw new Error(
        `pin ${source.commit} not found in ${source.repo}. ` +
          'Upstream may have rewritten history; update UPSTREAM.json to a commit that exists.',
      )
    }
    run(['log', '-1', '--format=%h %ad %s', '--date=short'], dir)
  }

  console.log('\ndone. upstream paths:')
  for (const name of names) {
    const source = sources[name]
    console.log(`  ${name}: ${source.subdir ? `${source.checkout}/${source.subdir}` : source.checkout}`)
  }
}

try {
  main()
} catch (error) {
  console.error(`\nsync failed: ${error.message}`)
  process.exit(1)
}