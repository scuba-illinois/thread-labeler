<script>
	import Comment from './Comment.svelte';
	let loadingComments = { comment: { body: "Loading comments" }, child_nodes: [] };

	//  - Root comment (not visible)	  
	//		> Parent comment
	//			> Child A
	//			> Child B
	//      > Sibling comment
	let responseExample = {		
			comment: {
				root: true,
			},
			child_nodes: [	
				{
					comment:
							{
								body: "Parent comment",
								metadata: "Parent value",
								id: "234vmlf"
							},
						
					child_nodes: 
							[
								{ 
									comment:
									{
										body: "Child A",
										metadata: "First child value",
										id: "gfdkl2346"
									},
									child_nodes: []
								},
								{ 
									comment:
									{
										body: "Child B",
										metadata: "Second child value",
										id: "786fgd543"
									},
									child_nodes: []
								}
							]
				},
				{
					comment: 
					{
						body: "Sibling comment",
						metadata: "A sibling",
						id: "12745bddc"
					},
					child_nodes: []
				}
		]
	}

	let root = responseExample; 
	// let root = loadingComments;

	let labelledToRemove = new Set();
	let showMetaInfo = new Set();
	
	let showInstructions = false;
	let showSettings = false;
	let saveUrl = "";
	let threadUrl = "";
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
		labelledToRemove.forEach((comment_id) => labels.push({ comment_id: comment_id, email: email }))
		console.log(JSON.stringify(labels))
		alert("Send a request to save labelling at this point!")
		if ( !saveUrl.length ) return;
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

	function downloadLabels() {
		alert("Send a request to download all the labels at this point!")
	}

	function loadNextThread() {
		if ( !threadUrl.length ) return;
		root = loadingComments;
		fetch(threadUrl)
	    .then(response => response.json())
	    .then(data => root = data)
	}

	loadNextThread();

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
	<p class="button" on:click={ loadNextThread }>Next thread</p>
	<p class:pressed={ showMetaInfo.has("metadata") } class="button" on:click={ () => addMetaInfo("metadata") }>Reveal metadata value for all comments</p>
	<p class:pressed={ showMetaInfo.has("conditionalMetadata") } class="button" on:click={ () => addMetaInfo("conditionalMetadata") }>Highlight comments for which the metadata value meets a condition</p>
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
				This section provides the user with instructions to use the tool			
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
	<a on:click="{downloadLabels}">Download all labelled comments</a>
	<label>
		Email (to keep track of who is labelling):
	 	<input type="text" placeholder="Email" bind:value={email}/>
   </label>
</div>

<Comment bind:labelled={ labelledToRemove } bind:metaInfo={showMetaInfo} comment={ root.comment } child_nodes={ root.child_nodes } />