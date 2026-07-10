<script lang="ts">
  import MetricCard from '$lib/components/MetricCard.svelte';
  import SectionCard from '$lib/components/SectionCard.svelte';

  export let data;

  function formatValue(value: number) {
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}`;
  }

  function listText(value: unknown) {
    return Array.isArray(value) ? value.join(', ') || 'None yet' : 'None yet';
  }
</script>

<svelte:head>
  <title>{data.report.title}</title>
</svelte:head>

<div class="space-y-6">
  <section class="panel rounded-[2.25rem] px-6 py-8 md:px-8">
    <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <p class="eyebrow">Summary</p>
        <h1 class="mt-3 font-display text-4xl text-white">{data.report.summary.trading_personality}</h1>
        <p class="mt-4 max-w-3xl text-base leading-8 text-mist/78">{data.report.summary.summary}</p>
      </div>
      <div class="rounded-[1.75rem] border border-glow/20 bg-glow/10 px-5 py-4">
        <p class="font-mono text-xs uppercase tracking-[0.24em] text-glow/80">Overall behavior score</p>
        <p class="mt-2 font-display text-4xl text-white">{data.report.summary.overall_behavior_score.toFixed(0)}</p>
      </div>
    </div>

    <div class="mt-6 grid gap-4 md:grid-cols-2">
      <div class="rounded-3xl border border-grid/60 bg-black/20 p-4">
        <p class="eyebrow">Main strength</p>
        <p class="mt-3 text-sm leading-7 text-mist/80">{data.report.summary.main_strength}</p>
      </div>
      <div class="rounded-3xl border border-grid/60 bg-black/20 p-4">
        <p class="eyebrow">Main weakness</p>
        <p class="mt-3 text-sm leading-7 text-mist/80">{data.report.summary.main_weakness}</p>
      </div>
    </div>
  </section>

  <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
    {#each data.report.metric_cards as card}
      <MetricCard name={card.name} score={card.score} explanation={card.explanation} />
    {/each}
  </section>

  <section class="grid gap-6 lg:grid-cols-[1fr_1fr]">
    <SectionCard eyebrow="Capital Flow" title="Month-by-month net movement">
      <div class="table-shell">
        <table class="min-w-full divide-y divide-grid/70 text-sm">
          <thead class="bg-black/20 text-left text-mist/60">
            <tr>
              <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Month</th>
              <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Net movement</th>
              <th class="px-4 py-3 font-mono text-xs uppercase tracking-[0.2em]">Context</th>
            </tr>
          </thead>
          <tbody>
            {#each data.report.capital_flow as item}
              <tr class="border-t border-grid/40">
                <td class="px-4 py-3">{item.label}</td>
                <td class="px-4 py-3 font-mono" class:text-signal={item.value >= 0} class:text-alarm={item.value < 0}>{formatValue(item.value)}</td>
                <td class="px-4 py-3 text-mist/75">{item.detail}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </SectionCard>

    <SectionCard eyebrow="Theme Drift" title="What themes keep showing up">
      <div class="space-y-4 text-sm leading-7 text-mist/78">
        <p><span class="text-white">Top added themes:</span> {listText(data.report.theme_drift.top_added_themes)}</p>
        <p><span class="text-white">Repeated themes:</span> {listText(data.report.theme_drift.repeated_themes)}</p>
        <p><span class="text-white">Top abandoned themes:</span> {listText(data.report.theme_drift.top_abandoned_themes)}</p>
      </div>
      <pre class="mt-4 overflow-x-auto rounded-3xl border border-grid/60 bg-black/20 p-4 font-mono text-xs text-mist/70">{JSON.stringify(data.report.theme_drift.themes_over_time ?? {}, null, 2)}</pre>
    </SectionCard>
  </section>

  <section class="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
    <SectionCard eyebrow="Needs Review" title="Trade review list">
      <div class="space-y-3">
        {#each data.report.trade_review_list as item}
          <a class="block rounded-3xl border border-grid/60 bg-black/20 p-4 transition hover:border-glow/35" href={`/ticker/${item.ticker}?reportId=${data.report.report_id}`}>
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p class="font-display text-lg text-white">{item.ticker}</p>
                <p class="mt-1 text-sm text-mist/75">{item.behavioral_signal}</p>
              </div>
              <div class="font-mono text-xs uppercase tracking-[0.2em] text-amberline">{item.review_priority} priority</div>
            </div>
            <p class="mt-3 text-sm leading-7 text-mist/80">{item.notes}</p>
          </a>
        {/each}
      </div>
    </SectionCard>

    <SectionCard eyebrow="Data Quality" title="What shaped this report">
      <div class="space-y-4 text-sm leading-7 text-mist/80">
        <p><span class="text-white">Parsed rows:</span> {data.report.data_quality.parsed_rows}</p>
        <p><span class="text-white">Warning rows:</span> {data.report.data_quality.warning_rows}</p>
        <p><span class="text-white">Unknown rows:</span> {data.report.data_quality.unknown_rows}</p>
        <p><span class="text-white">Missing keys:</span> {data.report.data_quality.missing_keys.join(', ') || 'None'}</p>
      </div>
      <div class="mt-4 rounded-3xl border border-grid/60 bg-black/20 p-4">
        <p class="eyebrow">Warnings</p>
        <ul class="mt-3 space-y-2 text-sm text-mist/75">
          {#each data.warnings.warnings.slice(0, 8) as warning}
            <li>{warning.warning_message}</li>
          {/each}
        </ul>
      </div>
    </SectionCard>
  </section>
</div>
