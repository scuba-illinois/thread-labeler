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
	span.moderator_action {
		background: rgba(252, 35, 35, 0.849);
	}
	span.agreement_score {
		background: rgb(41, 161, 51);
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

    .false_positive {
		background: rgb(245, 245, 112);
	}

    span.false_positive_label {
		background: rgb(230, 180, 73);
	}
	.false_negative, span.false_negative_label {
		background: rgb(245, 128, 112);
	}
</style>
<div>
	{#if !comment.root }
	<span class="comment_wrapper" on:click={ () => { toggleRemovedLabel(comment.id); } }>
		{#if metaInfo.has("author") }
			<span class="meta_info author">
				<a href="https://old.reddit.com/user/{ comment.author }/" target="_blank">{ comment.author }</a>
			</span>
		{/if}
		{#if metaInfo.has("agreement_score") }
			<span class="meta_info agreement_score">
				Agreement Score: { comment.agreement_score }
			</span>
		{/if}
		{#if metaInfo.has("banned_by") && comment.banned_by != "" }
			<span class="meta_info moderator_action">
				Removed by <a href="https://old.reddit.com/user/{ comment.banned_by }/" target="_blank">{ comment.banned_by }</a>
			</span>
		{/if}
		{#if metaInfo.has("false_negative") && parseFloat(comment.agreement_score) < 0.85 && comment.banned_by != "" }
			<span class="meta_info false_negative_label">
				False Negative
			</span>
		{/if}
		{#if metaInfo.has("false_postive") && parseFloat(comment.agreement_score) > 0.85 && comment.banned_by == "" }
			<span class="meta_info false_positive_label">
				False Positive
			</span>
		{/if}
		<span class:removed="{ labelled.has(comment.id) }"
		      class:false_positive="{ metaInfo.has("false_positive") && parseFloat(comment.agreement_score) >= 0.85 && comment.banned_by == "" }"
		      class:false_negative="{ metaInfo.has("false_negative") && parseFloat(comment.agreement_score) < 0.85 && comment.banned_by != "" }">
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
