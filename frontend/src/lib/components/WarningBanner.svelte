<script lang="ts">
  export let warnings: string[] = [];
</script>

{#if warnings.length}
  <aside class="rounded-3xl border border-amberline/30 bg-amberline/10 p-4 text-sm text-amberline">
    <p class="font-display text-base text-white">Some integrations are unavailable</p>
    <ul class="mt-3 space-y-2 text-mist/85">
      {#each warnings as warning}
        <li>{warning}</li>
      {/each}
    </ul>
  </aside>
{/if}

