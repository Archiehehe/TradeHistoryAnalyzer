<script lang="ts">
  import SectionCard from '$lib/components/SectionCard.svelte';
  import StatusPill from '$lib/components/StatusPill.svelte';
  import type { LayoutData } from '$lib/types';

  export let data: LayoutData;

  type IntegrationRow = {
    label: string;
    active: boolean;
    usage: string;
  };

  const rows: IntegrationRow[] = data.integrationStatus
    ? [
        { label: 'Gemini', active: data.integrationStatus.gemini_configured, usage: 'Final report narrative' },
        { label: 'Groq', active: data.integrationStatus.groq_configured, usage: 'Fast classification and fallback parser assistance' },
        { label: 'Alpha Vantage', active: data.integrationStatus.alpha_vantage_configured, usage: 'Primary market-data timing analysis' },
        { label: 'FMP', active: data.integrationStatus.fmp_configured, usage: 'Fallback market-data history' },
        { label: 'Database', active: data.integrationStatus.database_configured, usage: 'Uploads, rows, warnings, positions, and reports' },
        { label: 'Cloudflare R2', active: data.integrationStatus.r2_configured, usage: 'Production object storage backend' },
        { label: 'SEC User Agent', active: data.integrationStatus.sec_user_agent_configured, usage: 'SEC-compliant request header' }
      ]
    : [];
</script>

<svelte:head>
  <title>Integrations | TradeHistoryAnalyzer</title>
</svelte:head>

<div class="space-y-6">
  <SectionCard eyebrow="Integrations" title="Configured services">
    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {#each rows as row}
        <div class="rounded-3xl border border-grid/60 bg-black/20 p-4">
          <StatusPill label={row.label.toLowerCase()} active={row.active} />
        </div>
      {/each}
    </div>
  </SectionCard>

  <SectionCard eyebrow="Matrix" title="Service responsibilities">
    <div class="table-shell">
      <table class="min-w-full divide-y divide-grid/70 text-sm">
        <thead class="bg-black/20 text-left text-mist/60">
          <tr>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Service</th>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Configured</th>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Used for</th>
          </tr>
        </thead>
        <tbody>
          {#each rows as row}
            <tr class="border-t border-grid/40">
              <td class="px-4 py-3 text-white">{row.label}</td>
              <td class="px-4 py-3">{row.active ? 'Yes' : 'No'}</td>
              <td class="px-4 py-3 text-mist/78">{row.usage}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </SectionCard>
</div>
