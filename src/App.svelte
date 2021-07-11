<script>
	import Comment from './Comment.svelte';
	let loadingComments = { comment: { body: "Loading comments" }, child_nodes: [] };
	let loadingPost = { title: "Loading Post..", permalink: ""   };
	let root = loadingComments
	let post = loadingPost;

	let labelledToRemove = new Set();
	let showMetaInfo = new Set();
	
	let showInstructions = false;
	let showSettings = false;
	let saveUrl = "http://random-thread.crossmod.ml";
	let email = "";

	function toggleInstructions() {
		showInstructions = !showInstructions;
	}
	
	function toggleSettings() {
		showSettings = !showSettings;
	}

	function addMetaInfo(metaInfo) {
		if ( showMetaInfo.has(metaInfo) ) showMetaInfo.delete(metaInfo);
		else showMetaInfo.add(metaInfo);
		showMetaInfo = showMetaInfo;
	}

	function showRemovedIds() {
		console.log("Removed", labelledToRemove);
	}

	function saveLabels() {
		if ( !email.length ) {
			alert("Please enter an email address to help keep track of who is labelling");
			return;
		}
		showRemovedIds();
		if ( root === loadingComments ) return;
		let labels = []
		labelledToRemove.forEach((comment_id) => labels.push({ comment_id: comment_id, link_id: root.comment.id, email: email }))
		console.log(JSON.stringify(labels))
		fetch(`${saveUrl}/label/`, {
	     headers: {
	      'Accept': 'application/json',
	      'Content-Type': 'application/json'
	     },
	     method: 'POST',
	     body: JSON.stringify(labels)
	    })
		.then((response) => response.json())
		.then((data) => {
			console.log("Saving labels", data);
			alert("Saved labels!");
			labelledToRemove.clear();
		})
	}

	function loadPost(link_id) {
		post = loadingPost;
		fetch(`https://old.reddit.com/api/info.json?id=${link_id}`)
	  	.then(response => response.json())
	  	.then(data => {
			post = data.data.children[0].data;
		  });
	}

	function loadRandomThread() {
		root = loadingComments;
		fetch('http://random-thread.crossmod.ml')
	  	.then(response => response.json())
	  	.then(data => root = data)
		.then(_ => loadPost(root.comment.id));
	}

	loadRandomThread();

</script>

<style>
	.button_container {
		display: flex;
	}
	.button {
		margin: 5px;
		display: flex;
		width: fit-content;
		transition: all 0.2s linear;
		background: rgb(163, 163, 163);
		border-radius: 1px;
		padding: 10px;
		padding-left: 15px;
		padding-right: 15px;
		cursor: pointer;
		font-weight: bold;
	}
	.button:hover {
		opacity: 0.9;
		background: rgb(177, 176, 176);
	}

	.pressed {
		background: rgb(112, 112, 112);
	}

	.save {
		background: rgb(92, 204, 92);
	}
	.save:hover {
		opacity: 0.9;
		background: rgb(139, 231, 85);
	}

	.usage_container {
		background: rgb(235, 235, 235);
		font-style: italic;
		padding: 5px;
	}

	.action_link_container {
		display: flex;
		flex-direction: column;
	}
</style>

<div class="button_container">
	<p class="button" on:click={ loadRandomThread }>Show me another thread</p>
	<p class:pressed={ showMetaInfo.has("agreement_score") } class="button" on:click={ () => addMetaInfo("agreement_score") }>Reveal Crossmod Agreement Scores</p>
	<p class:pressed={ showMetaInfo.has("author") } class="button" on:click={ () => addMetaInfo("author") }>Reveal comment authors</p>
	<p class:pressed={ showMetaInfo.has("banned_by") } class="button" on:click={ () => addMetaInfo("banned_by") }>Reveal comments removed by moderators</p>
	<p class:pressed={ showMetaInfo.has("false_positive") } class="button" on:click={ () => addMetaInfo("false_positive") }>Highlight false positives</p>
	<p class:pressed={ showMetaInfo.has("false_negative") } class="button" on:click={ () => addMetaInfo("false_negative") }>Highlight false negatives</p>
	<p class="button save" on:click={ saveLabels }>Save my labelling!</p>
</div>
<div class="action_link_container">
	<a on:click={ toggleInstructions } href="#">
		{#if showInstructions }
			Understood!
		{:else }
			How do I use this tool?
		{/if}
	</a>
	{#if showInstructions }
	<div class="usage_container">
		<ul>
			<li>
				This tool shows you a randomly sampled discussion thread from Crossmod's reporting experiment data set.
				It is meant to help manually label comments a little more easily.
			</li>

			<li>
				To mark a comment as "removed", just click the text of the comment. You will see that the comment becomes struck-through to indicate this.
				To unmark a comment simply click again.
			</li>
			<li>
				Once you are done labelling comments, save your labels by clicking the "Save Labels button"
			</li>
			<li>
				The Reveal buttons add labels showing additional meta information about the comments, to help you better decide which comments to remove.
			</li>
			<li>
				To randomly sample another discussion thread, just hit the "Show me another thread button"
			</li>
			<li>
				False Positives: Comments removed by Crossmod that have not been removed by moderators (Highlighted in yellow)
			</li>
			<li>
				False Negatives: Comments removed by moderators that would not be removed by Crossmod (Highlighted in orange)
			</li>
		</ul>
	</div>
	{/if}
	<a on:click={ toggleSettings } href="#">
		{#if showSettings }
			Hide!
		{:else }
			Show dev settings
		{/if}
	</a>
	{#if showSettings }
	<div class="settings_container">
		<label>
	 	Server URL: 
	 	<input type="text" placeholder="server url format: http://example.com" bind:value={saveUrl}/>
    	</label>
	</div>
	{/if}
	<a href="{ saveUrl }/labels.csv">Download all labelled comments</a>
	<label>
		Email (to keep track of who is labelling):
	 	<input type="text" placeholder="Email" bind:value={email}/>
   </label>
</div>

<div>
	<a href="{ `https://old.reddit.com/${post.permalink}` }" target="_blank">
		<h3>{ post.title }</h3>
	</a>
</div>
<Comment bind:labelled={ labelledToRemove } bind:metaInfo={showMetaInfo} comment={ root.comment } child_nodes={ root.child_nodes } />