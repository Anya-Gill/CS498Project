const BASE_URL = "http://localhost:5000";

const responseArea = document.getElementById("response-area");
const statusBar    = document.getElementById("status-bar");

function setStatus(message, type = "") {
  statusBar.textContent = message;
  statusBar.className   = "status-bar " + type;
}

function setLoading(message = "Fetching...") {
  setStatus(message);
  responseArea.innerHTML = "";
}

/**
 * Renders a single tweet object as a card.
 */
function renderTweetCard(tweet) {
  const screenName   = tweet.user?.screen_name ?? "—";
  const createdAt    = tweet.created_at ?? "—";
  const text         = tweet.text ?? "—";
  const retweetCount = tweet.retweet_count ?? "—";
  const idStr        = tweet.id_str ?? "—";

  const card = document.createElement("div");
  card.className = "tweet-card";
  card.innerHTML = `
    <div class="tweet-meta">
      <span class="tweet-screen-name">@${screenName}</span>
      <span class="tweet-created-at">${createdAt}</span>
    </div>
    <div class="tweet-text">${text}</div>
    <div class="tweet-footer">
      <div class="tweet-footer-item">
        <span class="tweet-footer-label">Retweet count</span>
        <span class="tweet-footer-value">${retweetCount}</span>
      </div>
      <div class="tweet-footer-item">
        <span class="tweet-footer-label">ID</span>
        <span class="tweet-footer-value">${idStr}</span>
      </div>
    </div>
  `;
  return card;
}

/**
 * Endpoint 1 renderer
 */
function renderEndpointOne(data) {
  const tweets = data.data ?? [];
  if (!tweets.length) {
    responseArea.innerHTML = `<p class="state-message">No results returned.</p>`;
    return;
  }

  tweets.forEach(tweet => {
    responseArea.appendChild(renderTweetCard(tweet));
  });

  setStatus(`Showing ${tweets.length} result(s)`, "ok");
}

/**
 * Endpoint 2 renderer (raw JSON)
 */
function renderEndpointTwo(data) {
  const pre = document.createElement("pre");
  pre.className = "raw-json";
  pre.textContent = JSON.stringify(data, null, 2);
  responseArea.appendChild(pre);
  setStatus("Raw response from endpoint two.");
}

/**
 * ✅ Query 2: Hashtag Search
 */
function searchByHashtag() {
  const hashtag = document.getElementById("hashtagInput").value;

  setLoading("Searching tweets by hashtag...");

  fetch(`${BASE_URL}/tweets-by-hashtag?hashtag=${hashtag}`)
    .then(res => res.json())
    .then(data => {
      responseArea.innerHTML = "";

      if (!data.length) {
        responseArea.innerHTML = `<p class="state-message">No results found.</p>`;
        return;
      }

      data.forEach(tweet => {
        responseArea.appendChild(renderTweetCard(tweet));
      });

      setStatus(`Found ${data.length} tweets for #${hashtag}`, "ok");
    });
}

/**
 * ✅ Query 4: Replies
 */
function getReplies() {
  const tweetId = document.getElementById("tweetIdInput").value;

  setLoading("Fetching replies...");

  fetch(`${BASE_URL}/replies-to-tweet?tweet_id=${tweetId}`)
    .then(res => res.json())
    .then(data => {
      responseArea.innerHTML = "";

      if (!data.length) {
        responseArea.innerHTML = `<p class="state-message">No replies found.</p>`;
        return;
      }

      data.forEach(tweet => {
        responseArea.appendChild(renderTweetCard(tweet));
      });

      setStatus(`Found ${data.length} replies`, "ok");
    });
}

/**
 * ✅ OPTIONAL: Show sample hashtags (helps demo)
 */
function getHashtags() {
  setLoading("Fetching hashtags...");

  fetch(`${BASE_URL}/sample-hashtags`)
    .then(res => res.json())
    .then(data => {
      responseArea.innerHTML = "";

      if (!data.length) {
        responseArea.innerHTML = `<p class="state-message">No hashtags found.</p>`;
        return;
      }

      data.forEach(tag => {
        const el = document.createElement("div");
        el.className = "tweet-card";
        el.textContent = `#${tag}`;
        responseArea.appendChild(el);
      });

      setStatus(`Showing ${data.length} hashtags`, "ok");
    });
}

/**
 * Ping renderer
 */
function renderPing(data) {
  const status = data.status ?? "unknown";
  const tweet  = data.sample_tweet ?? null;
  const isOk   = status === "ok";

  const card = document.createElement("div");
  card.className = "ping-card";

  const statusRow = document.createElement("div");
  statusRow.className = "ping-status-row";
  statusRow.innerHTML = `
    <span class="ping-status-dot ${isOk ? "ok" : "error"}"></span>
    <span class="ping-status-text">status: ${status}</span>
    <span class="ping-status-label">sample tweet</span>
  `;
  card.appendChild(statusRow);

  if (tweet) {
    const tweetWrap = document.createElement("div");
    tweetWrap.className = "ping-tweet";
    tweetWrap.appendChild(renderTweetCard(tweet));
    card.appendChild(tweetWrap);
  }

  responseArea.appendChild(card);
  setStatus(`Ping returned: ${status}`, isOk ? "ok" : "error");
}

async function callEndpoint(which) {
  const endpointMap = {
    one:  "/endpoint-one",
    two:  "/endpoint-two",
    ping: "/ping",
  };

  setLoading(`Calling ${endpointMap[which]}...`);
  disableButtons(true);

  try {
    const response = await fetch(`${BASE_URL}${endpointMap[which]}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error ?? `HTTP ${response.status}`);
    }

    if (which === "one")  renderEndpointOne(data);
    if (which === "two")  renderEndpointTwo(data);
    if (which === "ping") renderPing(data);

  } catch (err) {
    responseArea.innerHTML = `<p class="state-message error">Error: ${err.message}</p>`;
    setStatus(`Request failed: ${err.message}`, "error");
  } finally {
    disableButtons(false);
  }
}

function disableButtons(state) {
  document.querySelectorAll("button").forEach(btn => btn.disabled = state);
}