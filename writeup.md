# Grey Cat the Flag: "seeteeeffed-in" Write-up

## Challenge Description
"CTFs are the best chance to connect with others. Network with others in this Grey Cat the Flag! But make sure to connect fast - the world resets every 5 mins."

## Summary
The goal of this web challenge is to extract the hidden "flag", a secret piece of text that proves we successfully hacked the application. To do this, we abused a vulnerability (a "bug" in the code) inside the database software the application runs on. This vulnerability allowed us to trick the database into giving us the secret flag.

## Step-by-Step Breakdown

### 1. Understanding the Application
The application is a simple social network where users can register, choose public and private usernames, and post messages. Looking closely at the source code provided in the challenge files, we noticed the application stores data in a PostgreSQL database and uses something called "Triggers".

Triggers are like automated rules in a database. For instance, if you change your username in your profile, a trigger might automatically update all your past posts to show your new username so the database stays consistent.

### 2. Identifying the Bug
By inspecting the database creation script (`init.sql`), we found a specific trigger:
```sql
CREATE TRIGGER player_usernames_refint_cascade
AFTER UPDATE OR DELETE ON player_usernames
FOR EACH ROW
EXECUTE FUNCTION check_foreign_key(1, 'cascade', 'username', 'user_sessions', 'username');
```
This rule says: "Whenever a user changes their username, update the `user_sessions` table so the user's session remains active under their new username."

At the same time, we noticed the challenge environment might be using a database version that has a known vulnerability: **CVE-2026-6637**.
This vulnerability exists in the `check_foreign_key` function and happens when a user types a specially crafted username. Because the database doesn't sanitize (clean up) the new username properly before updating related tables, we can perform a **SQL Injection**.

SQL Injection means we can "inject" our own database commands into the system. If we change our username to a malicious piece of text, the database will interpret it as a command instead of a normal name.

### 3. The Exploit
To get the flag, we followed these steps:

1. **Register a new account**: We created a user account with a random public and private username.
2. **Rename our profile**: We used the `/api/profile/private-rename` feature to change our private username.

Instead of choosing a normal new name, we used this malicious text:
`awbrethw', session_note = (SELECT flag FROM secrets LIMIT 1) -- `

#### What does this do?
When the database automatically updates our session record with our "new username", our injected code overrides another field in our session called the `session_note`. The `(SELECT flag FROM secrets LIMIT 1)` part commands the database to fetch the secret flag from the hidden `secrets` table and save it as our `session_note`.

### 4. Retrieving the Flag
Once we submitted this name change, the database executed our hidden command. When we checked our profile data again, our `session_note` had been updated from the default message to the secret flag!

**Flag:** `grey{refint_c4Scad3_Upd4t3_sq1_lnject10n}`