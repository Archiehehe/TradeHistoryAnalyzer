<script lang="ts">
  export let name: string;
  export let score: number;
  export let explanation: string;
</script>

<article class="panel rounded-3xl p-5">
  <div class="flex items-start justify-between gap-4">
    <div>
      <p class="eyebrow">Metric</p>
      <h3 class="mt-2 font-display text-lg text-white">{name}</h3>
    </div>
    <div class="rounded-2xl border border-glow/20 bg-glow/10 px-4 py-3 text-right">
      <p class="font-mono text-xs uppercase tracking-[0.24em] text-glow/80">Score</p>
      <p class="mt-1 font-display text-2xl text-white">{score.toFixed(0)}</p>
    </div>
  </div>
  <p class="mt-4 text-sm leading-6 text-mist/80">{explanation}</p>
</article>

