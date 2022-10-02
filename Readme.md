# L&F : A LOST & FOUND Support Community
> __CS50x Final Project Submission by @amWRit www.amritpuri.com.np__

# Demo
https://youtu.be/NwFCbfQZYqs

# About L&F
L&F is a social community to help people find their lost items or report found items. People can post about their lost or found items, browse through the L&F feed and check the listings. They can claim the lost item to be theirs or claim to have found a lost item.

Users can see a history of their posts and claims. Users can cancel claims, deny claims and delete posts. There is also a messaging feature for further confirmation of the claims based on photo proofs.

# Project Inspiration
I am in a few of the Facebook **Lost and Found** groups for pets where people post about their lost pets or post about a pet they have seen somewhere in their area. People also make a lost of post about their lost items, documents and even person in Facebook.

One similar incident happened with me a year back. I lost my wallet. Reporting it to the police wasn't the best idea as there is no such robust mechanism and guarantee that they will help in finding. So I took myself to Facebook. I requested a page with lots of followers to make a post about my wallet. But there was no response.

This idea about a Lost and Found platform had been in my mind for some time now. Ideally, I think it would be best as a mobile app. I also checked the app store and play store if there were any such apps. I couldn't find anything I was looking for. And I always wished there was some kind of app where I could go and search for my lost items.

### But why is it any different than a Facebook group?
I think Facebook has a great reach within the community. And I strongly believe they could integrate this feature into the groups. The only problem I see is when an item or a person is found. That original post about _lost item or person_ lingers around in the Facebook world as it is even though the item or person was already found. There is no way to do some kind of __update__ to the post so that it is marked as __FOUND__. And when people come across that original post, they know it has been found already.
I think Facebook could do this similar to the items __SOLD__ feature in their marketplace.

# Features
### Register
- New user can register by providing username, password, email and phone number.
- Validation has been done for username, password, email and phone number format.

### Login /Log Out
- User can login using their registered username and password.
- User can logout from a dropdown button by clicking on their username on navbar.

### L&F Index Page
- The index page shows all of the listings of the lost and found items posted by L&F registered users, sorted by date descending.
- Each post shows type (lost or found) and category (documents, jewellery, cycle, laptop, etc.), title of the post, description, date, location, current status (unclaimed, claimed or claim in progress), contact email and name of the user who made the post.
- In each post, user can claim the item posted by others or mark the post as 'claimed'.

#### Filter and Search
- Within the index listing page, user can filter the posts by type and/or category.
- Also the user can search by the name (searched for title of the post by LIKE in the database)
- The filter and search buttons are disabled until any filter option is selected or search text is provide.


### Post New
- User can make a new post about his/her/their lost/found item. They have to provide a photo, location, title, description and last seen location of the item.


### Claim
- User can claim an item. If the post is about a lost item that belongs to the user, the user can claim to have found that.
- If the post is about a found item, the user can claim that it belongs to them.
- When the user makes a claim, he/she/they have to provide a photo proof along with a message. The message and the photo is then shown to the other user who posted the item.


### Cancel Claim
- After a user has made a claim about an item, he/she/they can cancel the claim if they think they made a mistake.

### Deny Claim
- When the user who posted about the item receives a claim request from another user, he/she/they can deny the claim request if they don't find the proof valid.

### History
- The history page shows a listing of posts made and claim requests or claims completed by the logged in user.
- The user can delete the posts, cancel their current claims or deny claim requests made by other from this page.

### Messages
- There is also a messaging feature where users can chat about the item.
- There are two kinds of messages; Claim and Chat.
- The **Claim messages** are sent/received when the user makes/receives a claim request about an item.
- The **Chat messages** are normal conversation messages between two users about an item.

### About and Disclaimer Page
- There is an about page which has general short information about L&F community platform.
- The disclaimer page has short disclaimers on behalf of L&F.

### UI & UX
- The interface of the website is build around the blue color and its shades.
- The index, history and messages pages are built on the **feed** idea of social media pages where users keep scrolling to check listings.
- Flash messages help users understand whatever happens when they browse a page or click on buttons.
- Javascript confirmations are added to certain buttons to make sure the user wanted to do that action.

# Project Flow
- First I started with sketching out the design of website itself, what pages it will have, how it will look like, where will be the buttons and forms etc.
- Then I sketched out a simple block arrow diagram to see the flow of the website functionality (What happens after user logs in, what happens when user clicks on 'new post', what happens when user clicks on 'claim' button etc.)
- Once the workflow design was somehow concrete, I started working on the database, what tables were required and what fields were required within each table, how would one table interact with other table, if necessary, etc.
- I didn't want to invest a lot of time working on the login/logout feature and error handling. The distro code from PSET8 Fiance had amazing implementation of login/logut and error handling. So I chose to build my website upon that distro code itself.
- I started working on the very first index page then. I wanted to copy the idea from CS50's index page (https://cs50.me/cs50x) because I liked the style. I tried my ways. But it wasn't working out. So later I chose to make completely new and got help from Bootstrap's grid feature.
- I worked on the iterative development cycle, adding new changes in the new interation


### MVP
1. A website where user posts and the posts can be viewed in the __index page__.
2. Implement the __Claim/Mark as Claimed__ feature.
3. __History__ page to view user's posts and claims.
4. Adding a __messaging__ feature.
5. Add __actions on claims__ (denying, cancelling) and deleting posts.
6. Add a post specific detail page which could be reached by clicking on __ID__ of the post.
7. Add a __filter and search__ feature to the index page.
8. Add __flash messages__ instead of the meme apology page wherever suited.


# Challenges
The biggest challenge for me was adding the image uploading functionality. All of the other functions that I wanted in the website were pretty much clear and straightforward to me.

Users upload an image when making a post and also when sending a claim request photo proof. These images had to be saved in the project folders (server side).

I took help from Google to find out a very clearly guided page that helped me implement this functionality.
https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
This tutorial was a lifesaver for me.

The other not-so-big challenge was to be sure if I should include AJAX and JQUERY where needed or move them to server side codes. I am not much familar with them and find them pretty daunting. So, I was in dilemma if I should take time to learn about these things or not. At the end, I chose not to indulge with them for now.

# Possible Future Updates
- AJAX/JQUERY and Modals to decrease the routing and make it more user friendly
- Sub-categories (Example: Within Pets category, we could have dogs, cats, etc. And within them, we could have breeds of dogs.)
- Using some kind of location API to populate locations while adding a new post.
- Use of pagination in the listings
- Add account and privacy settings
- Feature to change password, phone number etc.
- Feature to implement user profile (photo, bio, user verificaiton etc.)
- Mobile friendly
- User roles and privileges (admins, moderators, etc.)
- Secure filenames for uploaded images
- Feature to add rewards when making a new post
- Refactor code implementations
- Remodel database
- UI improvements (always, of course!)

# Languages
- Python
- HTML
- Javascript
- CSS
- SQL


# Platforms and Libraries
- CS50 IDE
- Flask
- CS50 library
- SQLite
- Jinja
