<script lang="ts">
  export let title = '';
  export let eyebrow = '';
</script>

<section class="panel rounded-3xl p-5 md:p-6">
  {#if eyebrow}
    <p class="eyebrow">{eyebrow}</p>
  {/if}
  {#if title}
    <h2 class="mt-2 font-display text-xl text-white">{title}</h2>
  {/if}
  <div class="mt-4">
    <slot />
  </div>
</section>

