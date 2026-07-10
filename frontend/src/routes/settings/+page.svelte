<script lang="ts">
  import SectionCard from '$lib/components/SectionCard.svelte';
  import type { LayoutData } from '$lib/types';

  export let data: LayoutData;

  const envUsage = [
    ['GEMINI_API_KEY', 'Final plain-English behavior narrative in the backend AI router'],
    ['GROQ_API_KEY', 'Fast transaction classification, theme classification, and trade tagging in the backend parser/AI layer'],
    ['ALPHA_VANTAGE_API_KEY', 'Primary historical price lookups for timing context'],
    ['DATABASE_URL / NEON_DATABASE_URL', 'SQLAlchemy engine, uploads, transactions, warnings, reports, and positions'],
    ['SEC_USER_AGENT', 'Reserved for SEC-compliant filing enrichment and outbound SEC requests'],
    ['FMP_API_KEY', 'Fallback market-data router when Alpha Vantage is unavailable or sparse'],
    ['R2_*', 'Production object storage backend for uploaded files and raw documents']
  ];
</script>

<svelte:head>
  <title>Settings | TradeHistoryAnalyzer</title>
</svelte:head>

<div class="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
  <SectionCard eyebrow="Status" title="Current environment">
    <div class="space-y-4 text-sm leading-7 text-mist/80">
      <p><span class="text-white">API reachable:</span> {data.apiReachable ? 'Yes' : 'No'}</p>
      <p><span class="text-white">Environment:</span> {data.health?.environment ?? 'Unknown'}</p>
      <p><span class="text-white">Database configured:</span> {data.integrationStatus?.database_configured ? 'Yes' : 'No'}</p>
      <p><span class="text-white">Storage mode:</span> {data.integrationStatus?.r2_configured ? 'Cloudflare R2 prepared' : 'Local development storage'}</p>
    </div>
  </SectionCard>

  <SectionCard eyebrow="Env Map" title="Where each key is used">
    <div class="table-shell">
      <table class="min-w-full divide-y divide-grid/70 text-sm">
        <thead class="bg-black/20 text-left text-mist/60">
          <tr>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Key</th>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Usage</th>
          </tr>
        </thead>
        <tbody>
          {#each envUsage as [key, usage]}
            <tr class="border-t border-grid/40">
              <td class="px-4 py-3 font-mono text-xs uppercase tracking-[0.18em] text-glow/85">{key}</td>
              <td class="px-4 py-3 text-mist/78">{usage}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </SectionCard>
</div>

