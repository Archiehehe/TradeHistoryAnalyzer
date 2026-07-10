<script lang="ts">
  import { goto } from '$app/navigation';
  import { uploadPortfolioFiles, uploadTransactionFiles } from '$lib/api';
  import SectionCard from '$lib/components/SectionCard.svelte';
  import UploadDropzone from '$lib/components/UploadDropzone.svelte';

  let transactionFiles: File[] = [];
  let portfolioFiles: File[] = [];
  let notes = '';
  let error = '';
  let busy = false;

  async function handleSubmit() {
    error = '';
    if (!transactionFiles.length) {
      error = 'Transaction history files are required before parsing can begin.';
      return;
    }

    busy = true;
    try {
      const transactionUpload = await uploadTransactionFiles(transactionFiles, notes);
      const portfolioUpload = portfolioFiles.length ? await uploadPortfolioFiles(portfolioFiles, notes) : null;
      const search = portfolioUpload ? `?portfolio=${portfolioUpload.upload_id}` : '';
      await goto(`/review/${transactionUpload.upload_id}${search}`);
    } catch (caught) {
      error = caught instanceof Error ? caught.message : 'Upload failed.';
    } finally {
      busy = false;
    }
  }
</script>

<svelte:head>
  <title>Upload | TradeHistoryAnalyzer</title>
</svelte:head>

<div class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
  <SectionCard eyebrow="Input" title="Upload your history">
    <div class="space-y-5">
      <UploadDropzone
        bind:files={transactionFiles}
        label="Transaction history files"
        description="Required. Multiple broker CSV exports are supported, along with transaction PDFs that contain extractable tables."
      />
      <UploadDropzone
        bind:files={portfolioFiles}
        label="Current portfolio context"
        description="Optional. A Seeking Alpha portfolio CSV improves current holding status, conviction context, and open-versus-closed position checks."
        accept=".csv,.tsv,.txt"
      />
      <label class="block">
        <span class="eyebrow">Notes</span>
        <textarea bind:value={notes} class="mt-2 min-h-28 w-full rounded-3xl border border-grid bg-black/20 px-4 py-3 text-sm text-mist outline-none transition focus:border-glow/40" placeholder="Optional context about the account, broker export quirks, or date coverage."></textarea>
      </label>
      {#if error}
        <div class="rounded-3xl border border-alarm/30 bg-alarm/10 px-4 py-3 text-sm text-mist/80">{error}</div>
      {/if}
      <button class="rounded-full bg-glow px-6 py-3 font-display text-sm text-ink disabled:cursor-not-allowed disabled:bg-glow/40" type="button" disabled={busy} on:click={handleSubmit}>
        {#if busy}Uploading...{:else}Parse uploads{/if}
      </button>
    </div>
  </SectionCard>

  <SectionCard eyebrow="Guide" title="Before you upload">
    <ul class="space-y-3 text-sm leading-7 text-mist/80">
      <li>Keep original broker columns intact when possible. The parser maps common field variants automatically.</li>
      <li>Rows that cannot be normalized are never dropped silently; they stay visible in the review screen with specific warnings.</li>
      <li>PDF parsing is table-only. If a statement image does not expose extractable tables, the app will mark it unsupported instead of faking output.</li>
      <li>Optional integrations stay behind the backend boundary and never expose your secret keys to the browser.</li>
    </ul>
  </SectionCard>
</div>

