<script lang="ts">
  import '../app.css';

  import WarningBanner from '$lib/components/WarningBanner.svelte';
  import type { LayoutData } from '$lib/types';

  export let data: LayoutData;

  const navItems = [
    { href: '/', label: 'Home' },
    { href: '/upload', label: 'Upload' },
    { href: '/settings', label: 'Settings' },
    { href: '/integrations', label: 'Integrations' }
  ];
</script>

<div class="min-h-screen">
  <div class="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
    <header class="panel rounded-[2rem] px-5 py-4">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <a class="font-display text-2xl text-white" href="/">TradeHistoryAnalyzer</a>
          <p class="mt-1 text-sm text-mist/70">Upload your trades. See your patterns. Review your decisions.</p>
        </div>
        <nav class="flex flex-wrap items-center gap-2">
          {#each navItems as item}
            <a class="rounded-full border border-grid/70 px-4 py-2 font-mono text-xs uppercase tracking-[0.22em] text-mist/80 transition hover:border-glow/40 hover:text-glow" href={item.href}>
              {item.label}
            </a>
          {/each}
        </nav>
      </div>
    </header>

    <main class="flex-1 py-6">
      {#if !data.apiReachable}
        <div class="mb-6 rounded-3xl border border-alarm/30 bg-alarm/10 p-4 text-sm text-mist/80">
          The backend API could not be reached. Frontend pages are available, but live parsing and report generation will stay offline until the FastAPI service is running.
        </div>
      {/if}

      {#if data.integrationStatus}
        <div class="mb-6">
          <WarningBanner warnings={data.integrationStatus.unavailable_features} />
        </div>
      {/if}

      <slot />
    </main>

    <footer class="mt-8 rounded-[2rem] border border-grid/70 bg-black/20 px-5 py-4 text-sm leading-6 text-mist/65">
      This tool analyzes trading behavior from uploaded data. It does not provide investment advice, financial advice, or personalized buy/sell recommendations. Outputs may be incomplete or incorrect if uploaded files are incomplete or parsed incorrectly.
    </footer>
  </div>
</div>

