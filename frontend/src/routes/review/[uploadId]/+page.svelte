<script lang="ts">
  import { goto } from '$app/navigation';
  import { generateReport } from '$lib/api';
  import SectionCard from '$lib/components/SectionCard.svelte';

  export let data;

  let busy = false;
  let error = '';

  async function handleGenerate() {
    error = '';
    busy = true;
    try {
      const report = await generateReport({
        upload_id: data.uploadId,
        portfolio_upload_id: data.portfolioUploadId ?? undefined
      });
      await goto(`/report/${report.report_id}`);
    } catch (caught) {
      error = caught instanceof Error ? caught.message : 'Report generation failed.';
    } finally {
      busy = false;
    }
  }
</script>

<svelte:head>
  <title>Review Upload | TradeHistoryAnalyzer</title>
</svelte:head>

<div class="space-y-6">
  <section class="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
    <SectionCard eyebrow="Review" title="Parse preview">
      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-3xl border border-grid/60 bg-black/20 p-4">
          <p class="eyebrow">Transaction rows</p>
          <p class="mt-3 font-display text-3xl text-white">{data.preview.parsed_transaction_count}</p>
        </div>
        <div class="rounded-3xl border border-grid/60 bg-black/20 p-4">
          <p class="eyebrow">Warning rows</p>
          <p class="mt-3 font-display text-3xl text-white">{data.preview.warning_rows.length}</p>
        </div>
      </div>

      <div class="mt-6 grid gap-4 sm:grid-cols-2">
        <div>
          <p class="eyebrow">Detected files</p>
          <p class="mt-2 text-sm text-mist/80">{data.preview.detected_file_types.join(', ') || 'None'}</p>
        </div>
        <div>
          <p class="eyebrow">Date range</p>
          <p class="mt-2 text-sm text-mist/80">{data.preview.detected_date_range[0] ?? 'Unknown'} to {data.preview.detected_date_range[1] ?? 'Unknown'}</p>
        </div>
        <div>
          <p class="eyebrow">Tickers</p>
          <p class="mt-2 text-sm text-mist/80">{data.preview.detected_tickers.slice(0, 18).join(', ') || 'None detected yet'}</p>
        </div>
        <div>
          <p class="eyebrow">Currencies</p>
          <p class="mt-2 text-sm text-mist/80">{data.preview.detected_currencies.join(', ') || 'Not detected'}</p>
        </div>
        <div class="sm:col-span-2">
          <p class="eyebrow">Detected transaction types</p>
          <p class="mt-2 text-sm text-mist/80">{data.preview.detected_transaction_types.join(', ') || 'Not detected yet'}</p>
        </div>
      </div>
    </SectionCard>

    <SectionCard eyebrow="Action" title="Generate report">
      <p class="text-sm leading-7 text-mist/80">
        The report uses deterministic scoring first. If the AI providers are configured, the narrative layer adds plain-English interpretation on top of the same underlying metrics.
      </p>
      {#if error}
        <div class="mt-4 rounded-3xl border border-alarm/30 bg-alarm/10 px-4 py-3 text-sm text-mist/80">{error}</div>
      {/if}
      <button class="mt-6 rounded-full bg-glow px-6 py-3 font-display text-sm text-ink disabled:cursor-not-allowed disabled:bg-glow/40" type="button" disabled={busy} on:click={handleGenerate}>
        {#if busy}Generating...{:else}Generate behavior report{/if}
      </button>
      {#if data.portfolioUploadId}
        <p class="mt-4 text-sm text-mist/70">Portfolio context is attached to this review and will be included in the final analysis.</p>
      {/if}
    </SectionCard>
  </section>

  <section class="grid gap-6 lg:grid-cols-2">
    <SectionCard eyebrow="Warnings" title="Rows that need review">
      <div class="table-shell">
        <table class="min-w-full divide-y divide-grid/70 text-sm">
          <thead class="bg-black/20 text-left text-mist/60">
            <tr>
              <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">File</th>
              <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Row</th>
              <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Signal</th>
            </tr>
          </thead>
          <tbody>
            {#each data.preview.warning_rows as warning}
              <tr class="border-t border-grid/40">
                <td class="px-4 py-3 text-mist/70">{warning.source_file}</td>
                <td class="px-4 py-3 text-mist/70">{warning.row_number ?? '-'}</td>
                <td class="px-4 py-3 text-mist/85">{warning.warning_message}</td>
              </tr>
            {/each}
            {#if !data.preview.warning_rows.length}
              <tr>
                <td class="px-4 py-4 text-mist/60" colspan="3">No warning rows yet.</td>
              </tr>
            {/if}
          </tbody>
        </table>
      </div>
    </SectionCard>

    <SectionCard eyebrow="Availability" title="Disabled features">
      <ul class="space-y-3 text-sm leading-7 text-mist/80">
        {#each data.preview.disabled_features as feature}
          <li>{feature}</li>
        {/each}
        {#if !data.preview.disabled_features.length}
          <li>All configured integrations required for the current flow are available.</li>
        {/if}
      </ul>
    </SectionCard>
  </section>

  <SectionCard eyebrow="Unparsed" title="Rows that could not be normalized">
    <div class="table-shell">
      <table class="min-w-full divide-y divide-grid/70 text-sm">
        <thead class="bg-black/20 text-left text-mist/60">
          <tr>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Row payload</th>
          </tr>
        </thead>
        <tbody>
          {#each data.preview.unparsed_rows as row}
            <tr class="border-t border-grid/40">
              <td class="px-4 py-3">
                <pre class="overflow-x-auto whitespace-pre-wrap font-mono text-xs text-mist/70">{JSON.stringify(row, null, 2)}</pre>
              </td>
            </tr>
          {/each}
          {#if !data.preview.unparsed_rows.length}
            <tr>
              <td class="px-4 py-4 text-mist/60">No fully unparsed rows were detected.</td>
            </tr>
          {/if}
        </tbody>
      </table>
    </div>
  </SectionCard>
</div>

