<script>
	export let comment;
	export let child_nodes;
	export let labelled = new Set();
	export let metaInfo = new Set();

	function toggleRemovedLabel(comment_id) {
		if ( labelled.has(comment_id) ) labelled.delete(comment_id);
		else labelled.add(comment_id);
		labelled = labelled;
	}
</script>

<style>
	ul {
		padding: 0.2em 0 0 0.5em;
		margin: 0 0 0 0.5em;
		list-style: none;
		border-left: 1px solid #eee;
	}

	li {
		padding: 0.2em 0;
	}

	span.comment_wrapper {
		padding: 0 0 0 1em;
		background: url(https://icon-library.net/images/black-triangle-icon/black-triangle-icon-27.jpg) 0 0.5em no-repeat;
		background-size: 0.5em 0.5em;
		cursor: pointer;
	}

	span.meta_info {
		color: white;
		font-weight: bold;
		padding: 2px;
	}

	span.meta_info a {
		text-decoration: none;
		color:rgb(227, 237, 250);
	}

	span.removed {
		text-decoration: line-through;
	}

	span.metadata {
		background: rgb(105, 160, 233);
	}

	.conditional_metadata, span.conditional_metadata {
		background: rgb(245, 128, 112);
	}
</style>
<div>
	{#if !comment.root }
	<span class="comment_wrapper" on:click={ () => { toggleRemovedLabel(comment.id); } }>
		<!-- Displays metadata value that was hidden, no additional conditions need to be met to display this -->
		{#if metaInfo.has("metadata") }
			<span class="meta_info metadata">
				{ comment.metadata }
			</span>
		{/if}
		<!-- Highlights all comments which have the additional condition -->
		<span class:removed="{ labelled.has(comment.id) }"
		      class:conditional_metadata="{ metaInfo.has("conditionalMetadata") && comment.metadata.length > 12 }">
			{ comment.body }
		</span>
	</span>
	{/if}
	<ul>
		{#each child_nodes as comment}
			<li>
				<svelte:self {...comment} bind:labelled={labelled} bind:metaInfo={metaInfo}/>
			</li>
		{/each}
	</ul>

</div>
