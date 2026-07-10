<script lang="ts">
  export let label: string;
  export let active = false;

  $: pillClass = active
    ? 'inline-flex items-center gap-2 rounded-full border border-signal/30 px-3 py-1 font-mono text-xs uppercase tracking-[0.24em] text-signal shadow-[0_0_0_1px_rgba(137,255,93,0.2)]'
    : 'inline-flex items-center gap-2 rounded-full border border-alarm/30 px-3 py-1 font-mono text-xs uppercase tracking-[0.24em] text-alarm';
</script>

<span class={pillClass}>
  <span class={`h-2 w-2 rounded-full ${active ? 'bg-signal' : 'bg-alarm'}`}></span>
  {label}
</span>
