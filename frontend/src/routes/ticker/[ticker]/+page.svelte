<script lang="ts">
  import SectionCard from '$lib/components/SectionCard.svelte';

  export let data;
</script>

<svelte:head>
  <title>{data.tickerReport.ticker} | TradeHistoryAnalyzer</title>
</svelte:head>

<div class="space-y-6">
  <section class="panel rounded-[2.25rem] px-6 py-8 md:px-8">
    <p class="eyebrow">Ticker Timeline</p>
    <h1 class="mt-3 font-display text-4xl text-white">{data.tickerReport.ticker}</h1>
    <p class="mt-4 max-w-3xl text-base leading-8 text-mist/78">{data.tickerReport.behavioral_note}</p>
    <div class="mt-6 grid gap-4 md:grid-cols-3">
      <div class="rounded-3xl border border-grid/60 bg-black/20 p-4">
        <p class="eyebrow">First entry</p>
        <p class="mt-3 text-sm text-mist/80">{data.tickerReport.first_buy_date ?? 'Unknown'}</p>
      </div>
      <div class="rounded-3xl border border-grid/60 bg-black/20 p-4">
        <p class="eyebrow">Latest exit</p>
        <p class="mt-3 text-sm text-mist/80">{data.tickerReport.latest_sell_date ?? 'Unknown'}</p>
      </div>
      <div class="rounded-3xl border border-grid/60 bg-black/20 p-4">
        <p class="eyebrow">Current shares</p>
        <p class="mt-3 text-sm text-mist/80">{data.tickerReport.current_shares ?? 'Unavailable'}</p>
      </div>
    </div>
  </section>

  <SectionCard eyebrow="Timeline" title="All recorded activity">
    <div class="table-shell">
      <table class="min-w-full divide-y divide-grid/70 text-sm">
        <thead class="bg-black/20 text-left text-mist/60">
          <tr>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Date</th>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Action</th>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Quantity</th>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Price</th>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Net amount</th>
            <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Description</th>
          </tr>
        </thead>
        <tbody>
          {#each data.tickerReport.timeline as item}
            <tr class="border-t border-grid/40">
              <td class="px-4 py-3">{item.date ?? '-'}</td>
              <td class="px-4 py-3 uppercase text-mist/80">{item.action_normalized}</td>
              <td class="px-4 py-3">{item.quantity ?? '-'}</td>
              <td class="px-4 py-3">{item.price ?? '-'}</td>
              <td class="px-4 py-3">{item.net_amount ?? '-'}</td>
              <td class="px-4 py-3 text-mist/75">{item.description ?? '-'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </SectionCard>
</div>

