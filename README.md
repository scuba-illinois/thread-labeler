# Comment Thread Labeler

* This is a small front-end app written using the Svelte framework that allows you to display and label comments from a formatted JSON response.

---
## Context
* This tool was originally built to display and label randomly sampled Reddit comment threads. The user is able to see the original structure of the comment thread (as seen by a user on reddit.com) and also able to mark certain comments as "removed", to simulate a moderation action (i.e. apply a binary label).

---

## What can this do?

* This tool has the following functionality:
    * Display an arbitrary comment thread using a JSON object with a recursive format (an example of a JSON response that would produce valid output is provided below)
    * Allows the user to apply a binary label by clicking on each comment
    * Show / hide metadata related to each of the comments
    * Save labelled comments by sending it to an API endpoint.

---

## How do I run this?

* You need `npm` installed to run this app. [Here is a guide](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) to install npm if required.

* Install `svelte` and all the associated dependencies
```
npm install
```

* Run the development server
```
npm run dev
```
You should now be able to access the app at http://localhost:5000

---

## How do I modify this for my own use?
* This version of the app can be customized with a few small changes.
    ### Required Changes

    In `src/App.svelte`:
    * Comment out line 57 and uncomment line 58. This sets the default value to a loading indicator which is useful if the API response is slow.

    ```js
    // App.svelte
	57 // let root = responseExample; 
    58 let root = loadingComments;
    ```

    * Change line 65 to the URL of the endpoint you will use to save the labelling data. The data is sent as a stringified JSON object in a POST to the endpoint.
    ```js
    // App.svelte
    65 let saveUrl = "http://your-api.com/your-endpoint-name/"
    ``` 
     * The actual request to the endpoint specified in `saveUrl` is performed by the `saveLabels` function (`src/App.svelte:87`) that sends a POST request with a list of objects, each specifying the "removed" / labelled comments ids and the email of the current user.
    
    * Change line 66 to the URL of the endpoint you will use to retrieve the comment thread data. 
    ```js
    // App.svelte
    66 let threadUrl = "http://your-api.com/your-endpoint-name/"
    ``` 

     * The data that this endpoint returns is expected to be in the following format:
         ```json
         {
             /**
                 * A top level meta-comment which is root, that encapusulates all the actual comments in the thread is expected.
                 * This is indicated by the "root" key with a value of true, within the "comment" key for the top-level object
                 * The contents of this comment are not displayed.
             **/
             comment: // Required key
             {
                 root: true, // Required for the top level comment
                 body: "",
             }

             child_nodes: // Required key
             [
	           {
                    // We require a recursive JSON object that encapsulates the entire comment thread. This object should have certain "required" keys for the app to work correctly without any additional modifications.
	           	comment: // Required key
	           			{
                            /*
                                 This contains data pertaining to the current comment. 

                                 * Required keys: "body", "id"

                                 * This can also contain any number of other metadata keys that can be used to show/hide relevant companion information / highlight comments with certain values of metadata etc.
                                     * Please note that "metadata" is simply an example key - you can include any number of keys that you require. Refer to the metadata section of this README to see how you can use this additional data.

                            */
	           				body: "Parent comment", //Required key: Contains content for the comment 
	           				metadata: "Parent value",
	           				id: "234vmlf" //Required key: Used to keep track of which comments are labelled. We expect this to be globally unique identifiers available for each comment in the thread
	           			},

	           	child_nodes: // Required key
                            /*
                                This contains child objects with the same structure, indicating which child comments are nested under which parents. This recursive structure is used by the app to recreate the comment thread.
                            */
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
	           }

                    ]
         }
         ```

    ### Optional Changes

    * Metadata:

        * A metadata value is defined as any non-required keys included within the "comment" value of any given comment.
            ```json
            {
                comment: {
                    root: true,
                    body: "",
                }
                child_nodes: [
                    {
                        comment: {
                            body: "hello there",
                            optional_metadata_value: "general kenobi!" // This is an example of a metadata value
                        }

                        child_nodes: []
                    }
                ]
            }
            ```
        * Comments can have useful metadata that we may want to display / showcase. This tool provides a way to display this metadata and also highlight comments with metadata that meets certain specific conditions.
             ```js
             // src/App.svelte
             179 <p class:pressed={ showMetaInfo.has("metadata") } class="button" on:click={ () => addMetaInfo("metadata") }>Reveal metadata value for all comments</p>            
             ```
        * To toggle various metadata keys on and off, `App.svelte` maintains a set of "visible" metadata. Here we expect a metadata key called "metadata" to be visible when this button is pressed.

        * In `src/Comment.svelte`, line 60-64 - we display the metadata value if it has been toggled "on" by the user. CSS classes can also be created to customize how the metadata values are shown. Here, we have created a CSS class called metadata to customize how this label in the thread.

            ```html
    		60 {#if metaInfo.has("metadata") } //Key we inserted in the set of visible metadata in App.svelte
    		61	<span class="meta_info metadata">
    		62		{ comment.metadata }
    		63	</span>
    		64 {/if}
            ```
        * Additionally, it is possible to filter / highlight comments based on conditions which are applied on metadata values.
            * We add a key to the set of visible metadata in App.svelte
              ```html
                <!-- App.svelte -->

	            180 <p class:pressed={ showMetaInfo.has("conditionalMetadata") } class="button" on:click={ () => addMetaInfo("conditionalMetadata") }>Highlight comments for which the metadata value meets a condition</p>
              ```
              
            * We can perform a conditional check before adding a CSS class for the comments that meet the condition
               ```html
                <!-- Comment.svelte -->

		        66 <span class:removed="{ labelled.has(comment.id) }"
		        67      class:conditional_metadata="{ metaInfo.has("conditionalMetadata") && comment.metadata.length > 12 }"> <!-- We check a specific conditon before applying the CSS class for our new filter -->
		        68	{ comment.body }
		        69 </span>
              ```

    * Downloading labels:
        * If necessary, one could implement an endpoint that returns a list of all the removed comments for a given user / email address.
        * This functionality is stubbed out, and is left to the user to implement:
            ```js
                // App.svelte

	            115 function downloadLabels() {
	            116 	alert("Send a request to download all the labels at this point!")
	            117 }

            ```
---
* A more complete example, that was actually deployed, can be found in the `crossmod-labelling-experiment` branch within this repository. This is a more complex version of the app that was used to conduct an experiment that was a part of the [Crossmod project](https://github.com/ceshwar/crossmod). 

---
Bug reports and feature requests welcome!

    