<script>
import Comment from './Comment.svelte';

let loadedExperiment = false;
let currentPost = {};
let postDetails = {};
let currentComments = 0;
let currentPostsIndex = 0;
let currentPhasePosts = []
let currentPhaseComments = new Set();
let selected;
let removedComments = {};
let removalTime = {};
let phases = [
	{ id: 1, name: "Phase 1", postsSeen: 0, commentsSeen: 0, finished: false },
	{ id: 2, name: "Phase 2", postsSeen: 0, commentsSeen: 0, finished: false }
]
let labelledToRemove = new Set();

let participantId = "";
let experiment = {}
let completeExperimentEndpoint = () => `${endpointUrl}/participant/${participantId}/experiment/`
let currentPostEndpoint = (linkId) => `${endpointUrl}/participant/${participantId}/phase/${phaseId}/post/${linkId}/`
let endpointUrl = "http://label-thread.crossmod.ml/"
let phaseId = 1;
let loadingPost = { title: "Loading Post..", permalink: ""   };
let loadingComments = { comment: { body: "Loading comments" }, child_nodes: [] };
let root = loadingComments;

function setCurrentComments(){
	currentComments = 0;
	for ( let i = 0; i <= currentPostsIndex; ++i ) {
		let linkId = currentPhasePosts[i];
		currentComments += (experiment[currentPhase()].posts[linkId].length);
	}
}
function currentLinkId() { return currentPhasePosts[currentPostsIndex]; }
function currentPhase() { return `phase_${phaseId}`; }
function postsLength() { return currentPhasePosts.length }
function nextPost() { 
	currentPostsIndex = ( currentPostsIndex + 1 );
	if ( currentPostsIndex >= postsLength() ) {
		currentPostsIndex = postsLength() - 1;
		return;
	}
	setCurrentComments();
	phases[phaseId - 1].postsSeen = currentPostsIndex;
	phases[phaseId - 1].commentsSeen = currentComments;
	localStorage.setItem('phases', JSON.stringify(phases));
	loadPost(currentLinkId());
}
function previousPost() { 
	currentPostsIndex = Math.max(currentPostsIndex - 1, 0);
	loadPost(currentLinkId());
	setCurrentComments();
	phases[phaseId - 1].postsSeen = currentPostsIndex;
	phases[phaseId - 1].commentsSeen = currentComments;
	localStorage.setItem('phases', JSON.stringify(phases));
}

function loadPostDetails(link_id) {
	postDetails = loadingPost;
	fetch(`https://old.reddit.com/api/info.json?id=${link_id}`)
  	.then(response => response.json())
  	.then(data => {
		postDetails = data.data.children[0].data;
	  });
}

function loadPost(linkId) {
	console.log("Load link ID", linkId);
	console.log("Experiment:", experiment);
	fetch(currentPostEndpoint(linkId))
	.then(response => response.json())
	.then(data => {
		console.log(`Post ${linkId}`, data);
		currentPost = data;
		root = currentPost.post;
	})
	.then(_ => loadPostDetails(currentLinkId()))
}

function restoreLocal(participantId) {
	let oldParticipantId = localStorage.getItem('participantId');
	if ( oldParticipantId === null || parseInt(oldParticipantId) != participantId ) {
		clearLocal(false);
		return;	
	}
	let savedRemoved = localStorage.getItem('labelledToRemove');
	if ( savedRemoved === null ) return;
	removedComments = JSON.parse(savedRemoved);
	removedComments.forEach((comment) => labelledToRemove.add(comment.id));
	let savedRemovalTime = localStorage.getItem('removalTime');
	if ( savedRemovalTime !== null ) {
		removalTime = JSON.parse(savedRemovalTime);
	}
	
	let current = localStorage.getItem('currentPhase');
	if ( current === null ) {
		localStorage.setItem('currentPhase', String(1));
	}
	else {
		let progress = localStorage.getItem('phases');
		if ( progress === null ) return;
		phases = JSON.parse(progress);
		phaseId = parseInt(current);
		currentPostsIndex = phases[phaseId - 1].postsSeen;
		currentComments = phases[phaseId - 1].commentsSeen;
	}
}
function loadExperiment() {
	let currentParticipant = parseInt(participantId);
	if ( isNaN(currentParticipant) ) return;
	console.log("Current Participant:", participantId);
	restoreLocal(currentParticipant);
	localStorage.setItem('participantId', String(participantId));
	fetch(completeExperimentEndpoint())
	.then(response => response.json())
	.then(data => { 
		experiment = data;
		currentPhasePosts = Object.keys(experiment[currentPhase()]['posts']);
		currentPhasePosts.forEach( (linkId) => {
			experiment[currentPhase()]['posts'][linkId].forEach((commentId) => {
				currentPhaseComments.add(commentId);
			})
		})
		console.log("Comments to be checked", currentPhaseComments);
	})
	.then(_ => loadPost(currentLinkId()))
	.then(_ => loadedExperiment = true);
}
	
let showInstructions = false;
let showSettings = false;
let showRemovedComments = false;

function toggleInstructions() {
	showInstructions = !showInstructions;
}

function toggleSettings() {
	showSettings = !showSettings;
}

function toggleRemovedComments() {
	showRemovedComments = !showRemovedComments;
}
function generateCommentDetails(commentId){
	let phaseId = 1;

	for ( let i = phaseId; i <= 2; ++i ) {
		let phase = experiment[`phase_${i}`]
		let posts = phase.posts;
		let threaded = phase.threaded_interface;
		for (const [linkId, comments] of Object.entries(posts)) {
			console.log(comments);
			if ( comments.indexOf(commentId) != -1 ) {
				return {
					id: commentId,
					linkId: linkId,
					participant_id: participantId,
					threaded_interface: threaded,
					phase: i,
					removal_time: removalTime[commentId]
				}
			}
		}
	}
}
function changePhase() {
	console.log(phaseId);
	let previousPhaseId = ( phaseId == 2 ) ? 1 : 2;
	phases[previousPhaseId - 1].commentsSeen = currentComments;
	phases[previousPhaseId - 1].postsSeen = currentPostsIndex;
	localStorage.setItem('phases', JSON.stringify(phases));
	localStorage.setItem('currentPhase', String(phaseId));
	currentPostsIndex = phases[phaseId - 1].postsSeen;
	currentComments = phases[phaseId - 1].commentsSeen;
	currentPhasePosts = Object.keys(experiment[currentPhase()]['posts']);
	currentPhasePosts.forEach( (linkId) => {
		experiment[currentPhase()]['posts'][linkId].forEach((commentId) => {
			currentPhaseComments.add(commentId);
		})
	});
	loadPost(currentLinkId());
}
function saveLabelsManually(){
	saveLabels()
	.then((response) => response.json())
	.then((data) => {
		console.log("Saving labels", data);
		alert("Saved labels!");
	})
}

export let saveLabels = function() {
	console.log("Save labels");
	saveLocal();
	return saveLabelsOnServer();
}

function saveLabelsOnServer() {
	if ( root === loadingComments ) return;
	let labels = []
	labelledToRemove.forEach((comment_id) => {
		console.log("Labelled for", comment_id, generateCommentDetails(comment_id)); 
		labels.push(generateCommentDetails(comment_id));
	})
	console.log(JSON.stringify(labels))
	return fetch(`${endpointUrl}/label/`, {
     headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
     },
     method: 'POST',
     body: JSON.stringify(labels)
    })
}

function saveLocal() {
	if ( root === loadingComments ) return;
	let labels = []
	labelledToRemove.forEach((comment_id) => {
		console.log("Labelled for", comment_id, generateCommentDetails(comment_id)); 
		labels.push(generateCommentDetails(comment_id));
	})
	removedComments = labels;
	localStorage.setItem('removalTime', JSON.stringify(removalTime));
	localStorage.setItem('labelledToRemove', JSON.stringify(labels));
}

function clearLocal(showAlert = true) {
	localStorage.removeItem('currentPhase');
	localStorage.removeItem('removalTime');
	localStorage.removeItem('phases');
	localStorage.removeItem('labelledToRemove');
	localStorage.removeItem('participantId');
	if ( showAlert ) {
		alert("Removed locally saved data! The next time you label comments, all your data on the server will also be removed!");
	}
}
</script>

<style>
	.press{
		transition: 0.2s linear;
		cursor: pointer;
	}
	.press:hover {
		background: #9c9c9c;
	}

	.buttonList {
		list-style-type: none;
		display: flex;
		flex-direction: row;
	}

	.buttonList li {
		transition: all 0.2s linear;
		margin-left: 8px;
	}

	.buttonList li input{
		transition: 0.2s linear;
		cursor: pointer;
	}
	.buttonList li input:hover {
		background: #9c9c9c;
	}

	.downloadSaved {
		padding: 6px;
  	  	margin-left: 12px;
	}
	.progress {
		padding: 10px;	
		background: #ececec;
	}
</style>

{#if !loadedExperiment}
<div>
    <h1>Welcome to the Crossmod Labelling Experiment!</h1>
	<p>To start the experiment, enter your participant ID below!</p>
	<label>
		Enter your participant ID:
	 	<input type="text" placeholder="Participant ID" bind:value={participantId}/>
        <input type="button" on:click={ loadExperiment } value="Load Experiment!"/>
   </label>
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
					This tool will guide you in performing the labelling experiment. Comments meant to be moderated are highlighted in yellow (you cannot perform any moderation action on other comments).
				</li>
				<li>
					Please ensure you use the correct participant ID as this will change the set of comments / interface you see.
				</li>
				<li>
					You will be seeing 200 hundred comments in each phase and will mark a subset of these as "to be removed".
				</li>
   				<li>
   					To mark a comment as "removed", just click the text of the comment. You will see that the comment becomes struck-through to indicate this.
   					To unmark a comment simply click again.
   				</li>
				<li>
					Your labelling will be saved automatically as you the comments. There is also a button that will allow you to manually save in case you encounter any problems.
					Your current labelling state will also be saved in case you refresh the page / close the browser. (However you will have to enter your participant ID each time you access the page)
				</li>
				<li>
					You will be able to see the final output of your labelling by downloading the labelled CSV file (you can do this by clicking the "Download all labelled comments" button)
				</li>
				<li>
					You can also see your labelling locally saved in your browser's cache by clicking "Show locally saved labels" (this is displayed in JSON) in case you encounter problems with saving.
				</li>
				<li>
					Please keep in mind the <a href="https://old.reddit.com/r/futurology/wiki/rules">r/Futurology subreddit moderation rules</a> while you mark comments to be removed.
				</li>
				<li>
					Check <a href="https://www.notion.so/adishy/Crossmod-Labelling-Experiment-393b4498578345609c29c32f29d9427f">here</a> to read more about the rationale for the experiment
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
   	 	<input type="text" placeholder="server url format: http://example.com" bind:value={ endpointUrl }/>
       	</label>
   		<label>
   	 	Clear Locally Saved Data:			
        This removes any experiment saved labels from your browser's local cache. This will also clear any data saved on the server the next time you label a comment!
		( Use with care! )
   	 	<input class="press" type="button" on:click={ clearLocal } value="Remove Locally Saved Data"/>
       	</label>
   	</div>
   	{/if}
	</div>
</div>
{:else}
<div>
	<div class="options">
		<ul class="buttonList">
			<li>
				<select bind:value={phaseId} on:change="{changePhase}">
					{#each phases as phase }
						<option value={phase.id}>
							{phase.name}
						</option>
					{/each}
				</select>
			</li>
			<li>
				<input type="button" on:click={ previousPost } disabled="{ currentPostsIndex == 0 }" value="Previous Post"/>
			</li>
			<li>
				<input type="button" on:click={ nextPost } disabled="{ currentPostsIndex == postsLength() - 1 }" value="Next Post"/>
			</li>
			<li>
				<input type="button" value="Save Labelling!" on:click = { saveLabelsManually }/>
			</li>
   			<a class="downloadSaved" href="{ endpointUrl }/participant/{ participantId }/labels.csv">Download all labelled comments</a>
		</ul>
	</div>
	<div class="progress">
		<h3>Progress:</h3>
		<ul>
			<li>
				<p>You are on post: { currentPostsIndex + 1} of { postsLength() } total posts in this phase</p>
			</li>
			<li>
				<p>You have seen: { currentComments } of { experiment[currentPhase()].comments_count } total comments in this phase</p>
			</li>
			<li>
				<p>You are currently moderating comments in Phase { phaseId } of 2</p>
			</li>
			<li>
				<a href="#" on:click={ toggleRemovedComments }>
   					{#if showRemovedComments }
   						Hide!
   					{:else }
   						Show locally saved labels (in JSON format)
   					{/if}
				</a>
				{#if showRemovedComments }
				<pre>
					<code>
						{ JSON.stringify(removedComments, null, 3) }
					</code>
				</pre>
				{/if}
			</li>
		</ul>
	</div>
	<div class="displayPost">
		<div>
			<a href="{ `https://old.reddit.com/${postDetails.permalink}` }" target="_blank">
				<h3>{ postDetails.title }</h3>
			</a>
		</div>
		<Comment bind:labelled={ labelledToRemove } bind:removalTime={ removalTime } bind:save={ saveLabels } bind:currentPhaseComments={currentPhaseComments} comment={ root.comment } child_nodes={ root.child_nodes } />
	</div>
</div>
{/if}
