<script lang="ts">
  import SectionCard from '$lib/components/SectionCard.svelte';
  import StatusPill from '$lib/components/StatusPill.svelte';
  import type { LayoutData } from '$lib/types';

  export let data: LayoutData;

  const prompts = [
    'What kind of investor do my trades say I am?',
    'Am I overtrading?',
    'Which patterns deserve review?',
    'How has my behavior changed over time?'
  ];
</script>

<svelte:head>
  <title>TradeHistoryAnalyzer</title>
</svelte:head>

<section class="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
  <div class="panel rounded-[2.5rem] px-6 py-8 md:px-8 md:py-10">
    <p class="eyebrow">Behavior Audit</p>
    <h1 class="mt-4 max-w-3xl font-display text-4xl leading-tight text-white md:text-6xl">
      TradeHistoryAnalyzer turns your broker transaction history into a personal trading behavior report.
    </h1>
    <p class="mt-5 max-w-2xl text-base leading-8 text-mist/75 md:text-lg">
      Minimal input. Plain-English output. A personal trading-audit tool focused on behavioral signals, review priority, and possible patterns in your own history.
    </p>

    <div class="mt-8 flex flex-wrap gap-3">
      <a class="rounded-full bg-glow px-6 py-3 font-display text-sm text-ink transition hover:bg-white" href="/upload">Start upload</a>
      <a class="rounded-full border border-grid px-6 py-3 font-mono text-xs uppercase tracking-[0.24em] text-mist/75 hover:border-amberline/50 hover:text-amberline" href="/integrations">Check integrations</a>
    </div>

    <div class="mt-10 grid gap-3 sm:grid-cols-2">
      {#each prompts as prompt}
        <div class="rounded-3xl border border-grid/60 bg-black/20 px-4 py-4 text-sm text-mist/80">{prompt}</div>
      {/each}
    </div>
  </div>

  <div class="space-y-6">
    <SectionCard eyebrow="System" title="Runtime posture">
      <div class="flex flex-wrap gap-3">
        <StatusPill label="database" active={Boolean(data.integrationStatus?.database_configured)} />
        <StatusPill label="gemini" active={Boolean(data.integrationStatus?.gemini_configured)} />
        <StatusPill label="groq" active={Boolean(data.integrationStatus?.groq_configured)} />
        <StatusPill label="alpha" active={Boolean(data.integrationStatus?.alpha_vantage_configured)} />
      </div>
      <p class="mt-4 text-sm leading-6 text-mist/75">
        The frontend only sees safe status flags. Secret values stay server-side in the FastAPI configuration loader.
      </p>
    </SectionCard>

    <SectionCard eyebrow="Workflow" title="What happens next">
      <ol class="space-y-3 text-sm leading-6 text-mist/80">
        <li>1. Upload one or more transaction history files.</li>
        <li>2. Optionally add a Seeking Alpha portfolio CSV for current-position context.</li>
        <li>3. Review parsed rows, warnings, detected tickers, and disabled features.</li>
        <li>4. Generate a behavior report and inspect each ticker timeline.</li>
      </ol>
    </SectionCard>
  </div>
</section>

