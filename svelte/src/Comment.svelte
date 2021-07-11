<script>
	export let comment;
	export let removalTime;
	export let child_nodes;
	export let save;
	export let labelled = new Set();
	export let currentPhaseComments = new Set();

	function toggleRemovedLabel(comment_id) {
		if ( labelled.has(comment_id) ) labelled.delete(comment_id);
		else labelled.add(comment_id);
		removalTime[comment_id] = Date.now();
		save();
		labelled = labelled;
	}
</script>

<style>
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

	span.author {
		background: rgb(105, 160, 233);
	}
	ul {
		padding: 0.2em 0 0 0.5em;
		margin: 0 0 0 0.5em;
		list-style: none;
		border-left: 1px solid #eee;
	}

	li {
		padding: 0.2em 0;
	}

    .to_moderate {
		background: rgb(245, 245, 112);
	}
</style>
<div>
	{#if !comment.root }
	<span class="comment_wrapper"
		  on:click={ () => { if ( currentPhaseComments.has(comment.id) ) toggleRemovedLabel(comment.id); } }>
		<span class="meta_info author">
			<a href="https://old.reddit.com/user/{ comment.author }/" target="_blank">{ comment.author }</a>
		</span>
		<span class:removed="{ labelled.has(comment.id) }"
		  	  class:to_moderate="{ currentPhaseComments.has(comment.id)}">
			{ comment.body }
		</span>
	</span>
	{/if}
	<ul>
		{#each child_nodes as comment}
			<li>
				<svelte:self {...comment} bind:labelled={labelled} bind:removalTime={ removalTime } bind:save={save} bind:currentPhaseComments={currentPhaseComments}/>
			</li>
		{/each}
	</ul>

</div>
