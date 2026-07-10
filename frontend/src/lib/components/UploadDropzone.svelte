<script lang="ts">
  export let label: string;
  export let description: string;
  export let accept = '.csv,.pdf';
  export let multiple = true;
  export let files: File[] = [];

  let input: HTMLInputElement | null = null;
  let hovering = false;

  $: dropzoneClass = hovering
    ? 'rounded-[1.75rem] border border-dashed border-glow/50 bg-black/20 p-5 transition-colors'
    : 'rounded-[1.75rem] border border-dashed border-grid bg-black/20 p-5 transition-colors';

  function pickFiles() {
    input?.click();
  }

  function handleChange(event: Event) {
    const target = event.currentTarget as HTMLInputElement;
    files = Array.from(target.files ?? []);
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    hovering = false;
    files = Array.from(event.dataTransfer?.files ?? []);
  }
</script>

<div
  class={dropzoneClass}
  role="button"
  tabindex="0"
  aria-label={label}
  on:dragenter|preventDefault={() => (hovering = true)}
  on:dragover|preventDefault
  on:dragleave|preventDefault={() => (hovering = false)}
  on:drop={handleDrop}
  on:keydown={(event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      pickFiles();
    }
  }}
>
  <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
    <div>
      <p class="font-display text-lg text-white">{label}</p>
      <p class="mt-2 max-w-xl text-sm leading-6 text-mist/75">{description}</p>
    </div>
    <button class="rounded-full border border-glow/30 px-4 py-2 font-mono text-xs uppercase tracking-[0.24em] text-glow" type="button" on:click={pickFiles}>
      Select files
    </button>
  </div>

  <input bind:this={input} class="hidden" type="file" {accept} {multiple} on:change={handleChange} />

  <div class="mt-4 rounded-2xl bg-steel/70 p-4">
    {#if files.length}
      <ul class="space-y-2 text-sm text-mist/80">
        {#each files as file}
          <li class="flex items-center justify-between gap-3 rounded-2xl border border-grid/60 px-3 py-2">
            <span class="truncate">{file.name}</span>
            <span class="font-mono text-xs uppercase tracking-[0.18em] text-glow/80">{(file.size / 1024).toFixed(1)} KB</span>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="text-sm text-mist/55">Drop files here or use the selector. CSV and PDF transaction history are supported. Portfolio context expects CSV.</p>
    {/if}
  </div>
</div>
