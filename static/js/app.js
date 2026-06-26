const navButton = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");
const backButton = document.querySelector("[data-back]");

document.querySelectorAll(".flash").forEach((flash) => {
  window.setTimeout(() => {
    flash.classList.add("is-dismissing");
  }, 2500);
  window.setTimeout(() => {
    const wrap = flash.closest(".flash-wrap");
    flash.remove();
    if (wrap && !wrap.querySelector(".flash")) {
      wrap.remove();
    }
  }, 3100);
});

if (backButton) {
  backButton.addEventListener("click", () => {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.location.href = "/";
    }
  });
}

if (navButton && nav) {
  navButton.addEventListener("click", () => {
    nav.classList.toggle("open");
  });
}

const tagSelect = document.querySelector("[data-tag-select]");
const otherTagWrap = document.querySelector("[data-other-tag-wrap]");
const otherTag = document.querySelector("[data-other-tag]");

if (tagSelect && otherTagWrap && otherTag) {
  const syncOtherTag = () => {
    const isOther = tagSelect.value === "Other";
    otherTagWrap.classList.toggle("hidden", !isOther);
    otherTag.required = isOther;
    if (!isOther) {
      otherTag.value = "";
    }
  };
  tagSelect.addEventListener("change", syncOtherTag);
  syncOtherTag();
}

const errorLogSelect = document.querySelector("[data-error-log-select]");
const errorLogWrap = document.querySelector("[data-error-log-wrap]");
const errorLogInput = document.querySelector("[data-error-log-input]");

if (errorLogSelect && errorLogWrap && errorLogInput) {
  const syncErrorLog = () => {
    const needsLogs = errorLogSelect.value === "Yes";
    errorLogWrap.classList.toggle("hidden", !needsLogs);
    errorLogInput.required = needsLogs;
    if (!needsLogs) {
      errorLogInput.value = "";
    }
  };
  errorLogSelect.addEventListener("change", syncErrorLog);
  syncErrorLog();
}

document.querySelectorAll("[data-submit-on-change]").forEach((field) => {
  field.addEventListener("change", () => {
    field.form?.submit();
  });
});

const profileToggle = document.querySelector("[data-profile-toggle]");
const profileMenu = document.querySelector("[data-profile-menu]");
if (profileToggle && profileMenu) {
  profileToggle.addEventListener("click", () => {
    profileMenu.classList.toggle("open");
  });
  document.addEventListener("click", (event) => {
    if (!profileToggle.contains(event.target) && !profileMenu.contains(event.target)) {
      profileMenu.classList.remove("open");
    }
  });
}

const carousel = document.querySelector("[data-carousel]");
if (carousel) {
  const slides = [...carousel.querySelectorAll("[data-slide]")];
  const previous = carousel.querySelector("[data-slide-prev]");
  const next = carousel.querySelector("[data-slide-next]");
  let activeIndex = 0;

  const showSlide = (index) => {
    if (!slides.length) return;
    activeIndex = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      slide.classList.toggle("active", slideIndex === activeIndex);
    });
  };

  previous?.addEventListener("click", (event) => {
    event.preventDefault();
    showSlide(activeIndex - 1);
  });

  next?.addEventListener("click", (event) => {
    event.preventDefault();
    showSlide(activeIndex + 1);
  });

  window.setInterval(() => showSlide(activeIndex + 1), 7000);
}

document.querySelectorAll("[data-format]").forEach((button) => {
  button.addEventListener("click", () => {
    const editor = document.querySelector("[data-rich-editor]");
    if (!editor) return;
    const tag = button.dataset.format === "bold" ? "**" : "_";
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selected = editor.value.slice(start, end) || "text";
    editor.value = `${editor.value.slice(0, start)}${tag}${selected}${tag}${editor.value.slice(end)}`;
    editor.focus();
    editor.selectionStart = start + tag.length;
    editor.selectionEnd = start + tag.length + selected.length;
  });
});

const eventBrowser = document.querySelector("[data-event-browser]");
if (eventBrowser) {
  const triggers = [...eventBrowser.querySelectorAll("[data-event-trigger]")];
  const details = [...eventBrowser.querySelectorAll("[data-event-detail]")];

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const eventId = trigger.dataset.eventTrigger;
      triggers.forEach((item) => item.classList.toggle("active", item === trigger));
      details.forEach((detail) => {
        detail.classList.toggle("hidden", detail.dataset.eventDetail !== eventId);
      });
    });
  });
}

document.querySelectorAll("[data-inline-editor]").forEach((editor) => {
  const edit = editor.querySelector("[data-inline-edit]");
  const cancel = editor.querySelector("[data-inline-cancel]");
  const preview = editor.querySelector("[data-generated-preview]");
  const actions = editor.querySelector("[data-generated-actions]");
  const form = editor.querySelector("[data-generated-form]");

  edit?.addEventListener("click", () => {
    preview?.classList.add("hidden");
    actions?.classList.add("hidden");
    form?.classList.remove("hidden");
  });

  cancel?.addEventListener("click", () => {
    form?.classList.add("hidden");
    preview?.classList.remove("hidden");
    actions?.classList.remove("hidden");
  });
});

document.querySelectorAll("[data-reaction]").forEach((button) => {
  button.addEventListener("click", () => {
    const row = button.closest(".reaction-row");
    row?.querySelectorAll("[data-reaction]").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
  });
});

document.querySelectorAll("[data-comment-action]").forEach((button) => {
  button.addEventListener("click", () => {
    const answer = button.closest(".inline-answer, .answer-card");
    const form = answer?.querySelector("[data-comment-form]");
    if (form) {
      form.classList.toggle("hidden");
      form.querySelector("textarea")?.focus();
    } else {
      document.querySelector("[data-answer-input]")?.focus();
    }
  });
});

document.querySelectorAll("[data-copy-link]").forEach((button) => {
  button.addEventListener("click", async () => {
    const link = button.dataset.copyLink;
    if (!link) return;
    try {
      await navigator.clipboard.writeText(link);
      const original = button.textContent;
      button.textContent = "Copied";
      window.setTimeout(() => {
        button.textContent = original;
      }, 1600);
    } catch {
      const temp = document.createElement("input");
      temp.value = link;
      document.body.appendChild(temp);
      temp.select();
      document.execCommand("copy");
      temp.remove();
      button.textContent = "Copied";
    }
  });
});

const copyText = async (text) => {
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const temp = document.createElement("input");
    temp.value = text;
    document.body.appendChild(temp);
    temp.select();
    document.execCommand("copy");
    temp.remove();
  }
};

const attachPastedImages = (textarea) => {
  const form = textarea.closest("form");
  const input = form?.querySelector('input[type="file"][name="attachments"]');
  if (!input || typeof DataTransfer === "undefined") return;
  textarea.addEventListener("paste", (event) => {
    const images = [...(event.clipboardData?.files || [])].filter((file) => file.type.startsWith("image/"));
    if (!images.length) return;
    const transfer = new DataTransfer();
    [...input.files].forEach((file) => transfer.items.add(file));
    images.forEach((file, index) => {
      const extension = file.type.includes("png") ? "png" : "jpg";
      transfer.items.add(new File([file], `pasted-image-${Date.now()}-${index + 1}.${extension}`, { type: file.type }));
    });
    input.files = transfer.files;
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });
};

document.querySelectorAll("[data-paste-image-target]").forEach(attachPastedImages);

const qaApp = document.querySelector("[data-qa-app]");
if (qaApp) {
  const workspace = qaApp.querySelector("[data-qa-workspace]");
  const listRoot = qaApp.querySelector("[data-question-list]");
  const message = qaApp.querySelector("[data-qa-message]");
  let products = JSON.parse(document.getElementById("qa-products-data")?.textContent || "[]");
  const config = JSON.parse(document.getElementById("qa-config-data")?.textContent || "{}");
  let questions = JSON.parse(document.getElementById("qa-questions-data")?.textContent || "[]");
  const state = { status: "approved", productId: "", topicId: "", solved: "all", mode: "list", page: 1, pageSize: 20 };

  const escapeHtml = (value = "") => String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const showMessage = (text, tone = "success") => {
    if (!message) return;
    message.textContent = text;
    message.className = `qa-inline-message ${tone}`;
    window.setTimeout(() => message.classList.add("hidden"), 4200);
  };

  const requestJson = async (url, options = {}) => {
    const response = await fetch(url, {
      headers: { "X-Requested-With": "fetch", ...(options.headers || {}) },
      ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.ok === false) {
      throw new Error(data.message || "Something went wrong.");
    }
    return data;
  };

  const activeProduct = () => products.find((product) => String(product.id) === String(state.productId));
  const isIIQProduct = (product) => {
    const name = String(product?.name || "").toLowerCase().replace(/\s+/g, "");
    return name === "identityiq" || name === "iiq" || name.includes("identityiq");
  };
  const isOtherProduct = (product) => String(product?.slug || product?.name || "").toLowerCase().replace(/\s+/g, "") === "other";
  const productFilterLabel = (product) => product?.slug === "identity-security-cloud" ? "IdentityNow" : product?.name;

  const renderProductFilters = () => {
    const group = qaApp.querySelector(".qa-sidebar .qa-filter-group");
    if (!group) return;
    const total = products.reduce((sum, product) => sum + (product.count || 0), 0);
    const visibleProducts = products.filter((product) => !isOtherProduct(product));
    const otherTopics = products
      .filter(isOtherProduct)
      .flatMap((product) => product.topics || [])
      .filter((topic) => !["General", "Integration", "Troubleshooting"].includes(topic.name));
    group.innerHTML = `
      <h2>All Questions</h2>
      <button class="qa-side-link ${!state.productId && !state.topicId ? "active" : ""}" type="button" data-product-filter="">All Questions <strong data-all-count>${total}</strong></button>
      ${visibleProducts.map((product, index) => `
        <button class="qa-side-link ${String(state.productId) === String(product.id) ? "active" : ""}" type="button" data-product-filter="${product.id}">
          <span class="qa-dot ${["green", "violet", "orange", "slate"][index % 4]}"></span>
          <span>${escapeHtml(productFilterLabel(product))}</span>
          <strong>${product.count || 0}</strong>
        </button>
      `).join("")}
      ${otherTopics.map((topic) => `
        <button class="qa-side-link ${String(state.topicId) === String(topic.id) ? "active" : ""}" type="button" data-topic-filter="${topic.id}" data-sidebar-other-topic>
          <span class="qa-dot slate"></span>
          <span>${escapeHtml(topic.name)}</span>
          <strong>${topic.count || 0}</strong>
        </button>
      `).join("")}
    `;
  };

  const renderTopicFilters = () => {
    const wrap = qaApp.querySelector("[data-topic-filter-list]");
    const section = qaApp.querySelector("[data-topic-filter-wrap]");
    if (!wrap) return;
    const product = activeProduct();
    section?.classList.toggle("hidden", !product);
    if (!product) {
      wrap.innerHTML = "";
      return;
    }
    const topics = product.topics || [];
    const unique = new Map(topics.map((topic) => [topic.id, topic]));
    wrap.innerHTML = [...unique.values()].map((topic) => (
      `<button class="qa-side-link" type="button" data-topic-filter="${topic.id}"><span>${escapeHtml(topic.name)}</span><strong>${topic.count || 0}</strong></button>`
    )).join("");
  };

  const renderQuestionCard = (question) => `
    <article class="qa-question-card" data-open-question="${question.id}" tabindex="0" role="button">
      <div class="qa-card-content">
        <div class="qa-chip-row">
          <span class="qa-chip product">${escapeHtml(question.tags.product || "Product")}</span>
          <span class="qa-chip">${escapeHtml(question.tags.topic || "Topic")}</span>
          ${question.tags.version ? `<span class="qa-chip version">${escapeHtml(question.tags.version)}</span>` : ""}
          <span class="qa-chip">${escapeHtml(question.tags.difficulty || "Beginner")}</span>
          ${question.has_solution ? '<span class="qa-chip status">✔ Solution Available</span>' : '<span class="qa-chip unsolved">Unsolved</span>'}
          ${question.status !== "approved" ? '<span class="qa-chip review">Pending Review</span>' : ""}
        </div>
        <h2 class="qa-card-title">${escapeHtml(question.title)}</h2>
        <p>${escapeHtml(question.description).slice(0, 220)}</p>
        <div class="qa-card-meta">
          <span class="${question.answers_count ? "" : "zero"}">${question.answers_count} ${question.answers_count === 1 ? "reply" : "replies"}</span>
          <span>${question.views} views</span>
        </div>
        ${question.status === "rejected" && question.rejection_reason ? `<p class="qa-rejection-note">Rejected: ${escapeHtml(question.rejection_reason)}</p>` : ""}
      </div>
      <div class="qa-card-side">
        <div class="qa-asked"><span>Asked by</span><strong class="qa-mini-avatar">${escapeHtml(question.author.slice(0, 1))}</strong><span>${escapeHtml(question.author)}</span></div>
        <time>${escapeHtml(question.created)}</time>
        <div class="qa-card-actions">
          ${question.status === "pending" && config.isAdmin ? `
            <button class="qa-action publish" type="button" data-admin-action="approve" data-admin-question="${question.id}">Approve</button>
            <button class="qa-action reject" type="button" data-open-reject="${question.id}">Reject</button>
          ` : `
            ${question.has_solution ? '<button class="qa-action neutral" type="button" data-card-view-solution>View Solution</button>' : ""}
            <button class="qa-action neutral" type="button" data-copy-link-dynamic="${escapeHtml(question.url)}">Link</button>
          `}
        </div>
      </div>
      ${question.status === "pending" && config.isAdmin ? `
        <form class="qa-reject-form hidden" data-reject-form="${question.id}">
          <label>Reject reason
            <textarea name="reason" required rows="3" placeholder="Explain why this question is being rejected."></textarea>
          </label>
          <div class="qa-form-actions">
            <button class="ghost-button" type="button" data-cancel-reject>Cancel</button>
            <button class="qa-action reject" type="submit">Reject Question</button>
          </div>
        </form>
      ` : ""}
    </article>
  `;

  const renderList = () => {
    state.mode = "list";
    workspace.innerHTML = '<div class="qa-card-list" data-question-list></div>';
    const target = workspace.querySelector("[data-question-list]");
    if (!questions.length) {
      target.innerHTML = '<div class="empty big">No questions match this view.</div>';
      return;
    }
    const totalPages = Math.max(1, Math.ceil(questions.length / state.pageSize));
    state.page = Math.min(state.page, totalPages);
    const start = (state.page - 1) * state.pageSize;
    const visible = questions.slice(start, start + state.pageSize);
    target.innerHTML = visible.map(renderQuestionCard).join("") + (questions.length > state.pageSize ? `
      <nav class="qa-pagination" aria-label="Question pages">
        <button type="button" data-page-prev ${state.page === 1 ? "disabled" : ""}>Previous</button>
        <span>Page ${state.page} of ${totalPages}</span>
        <button type="button" data-page-next ${state.page === totalPages ? "disabled" : ""}>Next</button>
      </nav>
    ` : "");
  };

  const loadQuestions = async () => {
    const params = new URLSearchParams({ status: state.status, filter: state.solved });
    if (state.productId) params.set("product_id", state.productId);
    if (state.topicId) params.set("topic_id", state.topicId);
    const data = await requestJson(`${config.questionsApi}?${params}`);
    questions = data.questions || [];
    state.page = 1;
    renderList();
  };

  const refreshProducts = async () => {
    const data = await requestJson(config.productsApi);
    products = data.products || products;
    renderProductFilters();
    renderTopicFilters();
  };

  const renderReactions = (reactions, targetType, targetId) => `
    <div class="qa-reaction-picker">
      <button class="qa-reaction-trigger" type="button" aria-label="React">&hearts;</button>
      <div class="qa-reaction-menu">
      ${config.reactionChoices.map((choice) => {
        const reaction = reactions[choice.key] || { count: 0, selected: false };
        return `<button class="${reaction.selected ? "active" : ""}" type="button" data-react-type="${targetType}" data-react-id="${targetId}" data-reaction-type="${choice.key}" title="${escapeHtml(choice.label)}">
          <span>${choice.symbol}</span><strong>${reaction.count}</strong>
        </button>`;
      }).join("")}
      </div>
    </div>
  `;

  const renderReactionCounts = (reactions = {}) => {
    const counts = config.reactionChoices
      .map((choice) => ({ ...choice, count: reactions[choice.key]?.count || 0 }))
      .filter((choice) => choice.count > 0);
    if (!counts.length) return '<div class="qa-reaction-counts empty" aria-label="No reactions yet"></div>';
    return `<div class="qa-reaction-counts" aria-label="Reaction counts">${counts.map((choice) => (
      `<span title="${escapeHtml(choice.label)}">${choice.symbol} <strong>${choice.count}</strong></span>`
    )).join("")}</div>`;
  };

  const renderAttachments = (attachments) => {
    if (!attachments?.length) return "";
    const images = attachments.filter((file) => file.is_image);
    const files = attachments.filter((file) => !file.is_image);
    return `<div class="qa-attachments">
      ${images.length ? `<div class="qa-inline-images">${images.map((file) => `<img src="${file.url}" alt="${escapeHtml(file.filename)}">`).join("")}</div>` : ""}
      ${files.length ? `<strong>Attachments</strong><div>${files.map((file) => (
        `<a class="attachment-link" href="${file.url}" download>${escapeHtml(file.filename)} <span>Download</span></a>`
      )).join("")}</div>` : ""}
    </div>`;
  };

  const renderActionRow = (target, kind, question) => `
    <div class="qa-interaction-row">
      ${renderReactionCounts(target.reactions)}
      <div class="qa-interaction-actions">
        <button type="button" data-reply-focus>Reply</button>
        ${renderReactions(target.reactions, kind, target.id)}
        <button type="button" data-copy-link-dynamic="${escapeHtml(target.url || question.url)}">Link</button>
        ${kind === "question" ? `<button type="button" data-save-question="${question.id}">${question.is_saved ? "Saved" : "Save"}</button>` : "<button type=\"button\">Save</button>"}
        <button type="button" data-flag-action>Flag</button>
      </div>
    </div>
  `;

  const renderComments = (comments = []) => {
    if (!comments.length) return "";
    return `<div class="answer-comments">${comments.map((comment) => `
      <p><strong>${escapeHtml(comment.author)}</strong> <time>${escapeHtml(comment.created)}</time><span>${escapeHtml(comment.content)}</span></p>
    `).join("")}</div>`;
  };

  const renderAnswer = (answer, question) => `
    <article class="answer-card qa-answer-card ${question.solution_answer_id === answer.id ? "accepted" : ""}" id="answer-${answer.id}">
      <div class="qa-answer-top">
        ${question.solution_answer_id === answer.id ? '<span class="solution-badge">Accepted Solution</span>' : "<span></span>"}
        ${question.can_mark_solution ? `<button class="solution-action" type="button" data-mark-solution="${answer.id}">${question.solution_answer_id === answer.id ? "Unmark Solution" : "Mark as Solution"}</button>` : ""}
      </div>
      <div class="answer-author">
        <span class="avatar">${escapeHtml(answer.author.slice(0, 1))}</span>
        <div><strong>${escapeHtml(answer.author)}</strong><small>${escapeHtml(answer.created)}</small></div>
      </div>
      <div class="generated-content">${escapeHtml(answer.content)}</div>
      ${renderAttachments(answer.attachments)}
      <div class="qa-interaction-row">
        ${renderReactionCounts(answer.reactions)}
        <div class="qa-interaction-actions">
          <button type="button" data-answer-reply="${answer.id}">Reply</button>
          ${renderReactions(answer.reactions, "answer", answer.id)}
          <button type="button" data-copy-link-dynamic="${escapeHtml(`${question.url}#answer-${answer.id}`)}">Link</button>
          <button type="button" data-save-question="${question.id}">${question.is_saved ? "Saved" : "Save"}</button>
          <button type="button" data-flag-action>Flag</button>
        </div>
      </div>
      ${renderComments(answer.comments)}
      <form class="qa-comment-form hidden" data-comment-form="${answer.id}">
        <textarea name="body" rows="3" required placeholder="Write a response to this reply."></textarea>
        <button class="primary-button small" type="submit">Post Reply</button>
      </form>
    </article>
  `;

  const renderDetail = (question) => {
    state.mode = "detail";
    workspace.innerHTML = `
      <article class="qa-detail-card" data-current-question="${question.id}">
        <button class="qa-back-inline" type="button" data-back-to-list>Back to Questions</button>
        <h1>${escapeHtml(question.title)}</h1>
        <div class="qa-detail-meta">
          <span class="qa-mini-avatar">${escapeHtml(question.author.slice(0, 1))}</span>
          <span>${escapeHtml(question.author)}</span>
          <span>${escapeHtml(question.created_full)}</span>
          <span>${question.views} views</span>
        </div>
        <div class="qa-chip-row">
          <span class="qa-chip product">${escapeHtml(question.tags.product)}</span>
          <span class="qa-chip">${escapeHtml(question.tags.topic)}</span>
          ${question.tags.version ? `<span class="qa-chip version">${escapeHtml(question.tags.version)}</span>` : ""}
          <span class="qa-chip">${escapeHtml(question.tags.difficulty)}</span>
          ${question.has_solution ? '<span class="qa-chip status">✔ Solution Available</span>' : ""}
        </div>
        <div class="qa-detail-body"><p>${escapeHtml(question.description)}</p></div>
        ${question.has_logs ? `<pre class="qa-log-block">${escapeHtml(question.logs)}</pre>` : ""}
        ${renderAttachments(question.attachments)}
        ${renderActionRow(question, "question", question)}
        ${question.has_solution ? '<button class="qa-action publish" type="button" data-jump-solution>View Solution</button>' : ""}
        ${question.can_admin && question.status === "pending" ? `
          <div class="qa-review-actions">
            <button class="qa-action publish" type="button" data-admin-action="approve" data-admin-question="${question.id}">Approve</button>
            <button class="qa-action reject" type="button" data-open-reject="${question.id}">Reject</button>
          </div>
          <form class="qa-reject-form hidden" data-reject-form="${question.id}">
            <label>Reject reason
              <textarea name="reason" required rows="3" placeholder="Explain why this question is being rejected."></textarea>
            </label>
            <div class="qa-form-actions">
              <button class="ghost-button" type="button" data-cancel-reject>Cancel</button>
              <button class="qa-action reject" type="submit">Reject Question</button>
            </div>
          </form>` : ""}
      </article>
      <section class="qa-answer-section">
        <div class="qa-section-head"><h2>Replies</h2><span>${question.answers.length} ${question.answers.length === 1 ? "reply" : "replies"}</span></div>
        <div data-answer-list>
          ${question.answers.length ? question.answers.map((answer) => renderAnswer(answer, question)).join("") : '<p class="empty">No comments yet. Be the first to comment!</p>'}
        </div>
      </section>
      <form class="form-card answer-form qa-form-card qa-inline-answer-form" data-reply-form enctype="multipart/form-data">
        <h2>Your Reply</h2>
        ${config.isAuthenticated ? `
          <textarea name="content" required rows="4" placeholder="Share an answer, workaround, or clarifying question."></textarea>
          <input type="file" name="attachments" multiple accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.zip">
          <button class="primary-button" type="submit">Post Reply</button>` : `
          <p>Sign in to reply.</p><a class="primary-button" href="${config.loginUrl}">Sign in</a>`}
      </form>
    `;
  };

  const openQuestion = async (id, jumpSolution = false) => {
    const data = await requestJson(`${config.detailApiBase}${id}`);
    renderDetail(data.question);
    window.scrollTo({ top: 0, behavior: "instant" });
    if (jumpSolution && data.question.solution_answer_id) {
      document.getElementById(`answer-${data.question.solution_answer_id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };

  const renderAskForm = () => {
    if (!config.isAuthenticated) {
      window.location.href = config.loginUrl;
      return;
    }
    state.mode = "ask";
    workspace.innerHTML = `
      <section class="qa-ask-panel inline">
        <div class="qa-ask-panel-head"><h2>Ask Question</h2></div>
        <form class="qa-embedded-form" data-ask-form enctype="multipart/form-data">
          <div class="qa-form-grid">
            <label>Product *<select name="product_id" required data-ask-product><option value="">Select product</option>${products.map((product) => `<option value="${product.id}">${escapeHtml(product.name)}</option>`).join("")}</select></label>
            <label data-version-wrap>Version<select name="version_id" data-ask-version><option value="">Select version</option></select></label>
          </div>
          <label class="hidden" data-new-product-wrap>Product Name *<input name="new_product" data-new-product placeholder="Enter product name"></label>
          <div class="qa-form-grid">
            <label>Topic *<select name="topic_id" required data-ask-topic><option value="">Select topic</option></select></label>
            <label>Difficulty<select name="difficulty">${config.difficulties.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`).join("")}</select></label>
          </div>
          <label class="hidden" data-new-topic-wrap>Create New Topic<input name="new_topic" data-new-topic></label>
          <label class="hidden" data-new-version-wrap>Other Version<input name="new_version" data-new-version placeholder="Example: 8.6"></label>
          <label>Question Title *<input name="title" required minlength="10"></label>
          <label>Description *<textarea name="description" required minlength="20" rows="6" data-paste-image-target></textarea></label>
          <label>Do you have logs?<select name="has_logs" data-has-logs><option value="No">No</option><option value="Yes">Yes</option></select></label>
          <label class="hidden" data-logs-wrap>Logs<textarea name="logs" rows="5" data-logs-input></textarea></label>
          <label>Attachments (.pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.zip)<input type="file" name="attachments" multiple data-dedupe-files accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.zip"></label>
          <div class="qa-file-list" data-file-list></div>
          <div class="qa-form-actions"><button class="ghost-button" type="button" data-back-to-list>Cancel</button><button class="primary-button" type="submit">Submit for Review</button></div>
        </form>
      </section>`;
    syncAskOptions();
    workspace.querySelectorAll("[data-paste-image-target]").forEach(attachPastedImages);
  };

  const syncAskOptions = () => {
    const form = workspace.querySelector("[data-ask-form]");
    if (!form) return;
    const productSelect = form.querySelector("[data-ask-product]");
    const versionSelect = form.querySelector("[data-ask-version]");
    const versionWrap = form.querySelector("[data-version-wrap]");
    const newVersionWrap = form.querySelector("[data-new-version-wrap]");
    const newVersion = form.querySelector("[data-new-version]");
    const topicSelect = form.querySelector("[data-ask-topic]");
    const newTopicWrap = form.querySelector("[data-new-topic-wrap]");
    const newTopic = form.querySelector("[data-new-topic]");
    const newProductWrap = form.querySelector("[data-new-product-wrap]");
    const newProduct = form.querySelector("[data-new-product]");
    const product = products.find((item) => String(item.id) === productSelect.value);
    const selectedOtherProduct = isOtherProduct(product);
    const showVersion = isIIQProduct(product);
    versionWrap.classList.toggle("hidden", !showVersion);
    versionSelect.disabled = !showVersion;
    newVersionWrap.classList.add("hidden");
    newVersion.required = false;
    if (!showVersion) {
      versionSelect.innerHTML = '<option value="">Select version</option>';
      newVersion.value = "";
    } else {
      const preferred = ["8.5", "8.4", "8.3"];
      const versions = product?.versions || [];
      const ordered = [
        ...preferred.map((label) => versions.find((version) => version.label === label)).filter(Boolean),
        ...versions.filter((version) => !preferred.includes(version.label)),
      ];
      versionSelect.innerHTML = '<option value="">Select version</option>' + ordered.map((version) => `<option value="${version.id}">${escapeHtml(version.label)}</option>`).join("") + '<option value="Other">Other</option>';
    }
    topicSelect.innerHTML = '<option value="">Select topic</option>' + (product?.topics || []).map((topic) => `<option value="${topic.id}">${escapeHtml(topic.name)}</option>`).join("") + '<option value="Other">Other</option>';
    newProductWrap.classList.toggle("hidden", !selectedOtherProduct);
    newProduct.required = selectedOtherProduct;
    if (!selectedOtherProduct) newProduct.value = "";
    if (selectedOtherProduct) topicSelect.value = "Other";
    const isOther = topicSelect.value === "Other" || selectedOtherProduct;
    newTopicWrap.classList.toggle("hidden", !isOther);
    newTopic.required = isOther;
    if (!isOther) newTopic.value = "";
    topicSelect.required = !selectedOtherProduct;
    topicSelect.disabled = selectedOtherProduct;
  };

  qaApp.addEventListener("click", async (event) => {
    const ask = event.target.closest("[data-show-ask]");
    if (ask) {
      event.preventDefault();
      renderAskForm();
      return;
    }
    const back = event.target.closest("[data-back-to-list]");
    if (back) {
      event.preventDefault();
      if (window.history.length > 1) {
        window.history.back();
      } else {
        await loadQuestions();
      }
      return;
    }
    const productFilter = event.target.closest("[data-product-filter]");
    if (productFilter) {
      state.productId = productFilter.dataset.productFilter;
      state.topicId = "";
      qaApp.querySelectorAll("[data-product-filter]").forEach((button) => button.classList.toggle("active", button === productFilter));
      qaApp.querySelectorAll("[data-sidebar-other-topic]").forEach((button) => button.classList.remove("active"));
      qaApp.querySelectorAll("[data-topic-filter]").forEach((button) => button.classList.toggle("active", !button.dataset.topicFilter));
      renderTopicFilters();
      await loadQuestions();
      return;
    }
    const topicFilter = event.target.closest("[data-topic-filter]");
    if (topicFilter) {
      if (topicFilter.matches("[data-sidebar-other-topic]")) {
        state.productId = "";
        qaApp.querySelectorAll("[data-product-filter]").forEach((button) => button.classList.remove("active"));
      }
      state.topicId = topicFilter.dataset.topicFilter;
      qaApp.querySelectorAll("[data-topic-filter]").forEach((button) => button.classList.toggle("active", button === topicFilter));
      await loadQuestions();
      return;
    }
    const statusFilter = event.target.closest("[data-status-filter]");
    if (statusFilter) {
      state.status = statusFilter.dataset.statusFilter;
      qaApp.querySelectorAll("[data-status-filter]").forEach((button) => button.classList.toggle("active", button === statusFilter));
      await loadQuestions();
      return;
    }
    const prev = event.target.closest("[data-page-prev]");
    if (prev && state.page > 1) {
      state.page -= 1;
      renderList();
      return;
    }
    const next = event.target.closest("[data-page-next]");
    if (next && state.page < Math.ceil(questions.length / state.pageSize)) {
      state.page += 1;
      renderList();
      return;
    }
    const card = event.target.closest("[data-open-question]");
    if (card && !event.target.closest("button, a, input, textarea, select, form")) {
      await openQuestion(card.dataset.openQuestion);
      history.pushState({ qaMode: "detail", questionId: card.dataset.openQuestion }, "", `?question_id=${card.dataset.openQuestion}`);
      return;
    }
    const viewSolution = event.target.closest("[data-card-view-solution]");
    if (viewSolution) {
      const cardNode = viewSolution.closest("[data-open-question]");
      await openQuestion(cardNode.dataset.openQuestion, true);
      return;
    }
    const copy = event.target.closest("[data-copy-link-dynamic]");
    if (copy) {
      await copyText(copy.dataset.copyLinkDynamic);
      showMessage("Link copied");
      return;
    }
    const reply = event.target.closest("[data-reply-focus]");
    if (reply) {
      workspace.querySelector("[data-reply-form] textarea")?.focus();
      return;
    }
    const answerReply = event.target.closest("[data-answer-reply]");
    if (answerReply) {
      const form = workspace.querySelector(`[data-comment-form="${answerReply.dataset.answerReply}"]`);
      form?.classList.toggle("hidden");
      form?.querySelector("textarea")?.focus();
      return;
    }
    const flag = event.target.closest("[data-flag-action]");
    if (flag) {
      showMessage("Flagged for review.");
      return;
    }
    const reaction = event.target.closest("[data-react-type]");
    if (reaction) {
      if (!config.isAuthenticated) {
        window.location.href = config.loginUrl;
        return;
      }
      const url = reaction.dataset.reactType === "question"
        ? `${config.detailApiBase}${reaction.dataset.reactId}${config.questionReactionSuffix}`
        : `${config.answerReactionBase}${reaction.dataset.reactId}/reactions`;
      const formData = new FormData();
      formData.set("reaction_type", reaction.dataset.reactionType);
      await requestJson(url, { method: "POST", body: formData });
      const current = workspace.querySelector("[data-current-question]")?.dataset.currentQuestion;
      if (current) await openQuestion(current);
      return;
    }
    const save = event.target.closest("[data-save-question]");
    if (save) {
      await requestJson(`${config.detailApiBase}${save.dataset.saveQuestion}${config.saveSuffix}`, { method: "POST", body: new FormData() });
      await openQuestion(save.dataset.saveQuestion);
      showMessage("Saved questions are available in your profile.");
      return;
    }
    const solution = event.target.closest("[data-mark-solution]");
    if (solution) {
      const data = await requestJson(`${config.answerReactionBase}${solution.dataset.markSolution}${config.solutionSuffix}`, { method: "POST", body: new FormData() });
      renderDetail(data.question);
      showMessage("Solution updated");
      return;
    }
    const jump = event.target.closest("[data-jump-solution]");
    if (jump) {
      const id = workspace.querySelector("[data-current-question]")?.dataset.currentQuestion;
      const question = await requestJson(`${config.detailApiBase}${id}`);
      document.getElementById(`answer-${question.question.solution_answer_id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    const admin = event.target.closest("[data-admin-action]");
    if (admin) {
      await requestJson(`${config.approveBase}${admin.dataset.adminQuestion}/${admin.dataset.adminAction}`, { method: "POST", body: new FormData() });
      showMessage(admin.dataset.adminAction === "approve" ? "Question approved and published." : "Question rejected.");
      await loadQuestions();
    }
    const openReject = event.target.closest("[data-open-reject]");
    if (openReject) {
      const form = workspace.querySelector(`[data-reject-form="${openReject.dataset.openReject}"]`);
      form?.classList.remove("hidden");
      form?.querySelector("textarea")?.focus();
      return;
    }
    const cancelReject = event.target.closest("[data-cancel-reject]");
    if (cancelReject) {
      cancelReject.closest("[data-reject-form]")?.classList.add("hidden");
      return;
    }
  });

  qaApp.addEventListener("change", async (event) => {
    if (event.target.matches("[data-solved-filter]")) {
      state.solved = event.target.value;
      await loadQuestions();
    }
    if (event.target.matches("[data-ask-product]")) syncAskOptions();
    if (event.target.matches("[data-ask-topic]")) {
      const form = event.target.closest("form");
      const wrap = form.querySelector("[data-new-topic-wrap]");
      const input = form.querySelector("[data-new-topic]");
      const isOther = event.target.value === "Other";
      wrap.classList.toggle("hidden", !isOther);
      input.required = isOther;
      if (!isOther) input.value = "";
    }
    if (event.target.matches("[data-ask-version]")) {
      const form = event.target.closest("form");
      const wrap = form.querySelector("[data-new-version-wrap]");
      const input = form.querySelector("[data-new-version]");
      const isOther = event.target.value === "Other";
      wrap.classList.toggle("hidden", !isOther);
      input.required = isOther;
      if (!isOther) input.value = "";
    }
    if (event.target.matches("[data-has-logs]")) {
      const form = event.target.closest("form");
      const needsLogs = event.target.value === "Yes";
      form.querySelector("[data-logs-wrap]").classList.toggle("hidden", !needsLogs);
      form.querySelector("[data-logs-input]").required = needsLogs;
      if (!needsLogs) form.querySelector("[data-logs-input]").value = "";
    }
    if (event.target.matches("[data-dedupe-files]")) {
      const files = [...event.target.files];
      const names = new Set();
      const duplicates = files.filter((file) => {
        const key = `${file.name}-${file.size}`;
        if (names.has(key)) return true;
        names.add(key);
        return false;
      });
      if (duplicates.length) showMessage("Duplicate files were detected. The server will skip duplicates.", "error");
      const list = event.target.closest("form").querySelector("[data-file-list]");
      list.innerHTML = files.map((file) => {
        if (file.type.startsWith("image/")) {
          return `<span class="qa-file-preview"><img src="${URL.createObjectURL(file)}" alt="">${escapeHtml(file.name)}</span>`;
        }
        return `<span>${escapeHtml(file.name)}</span>`;
      }).join("");
    }
  });

  qaApp.addEventListener("submit", async (event) => {
    const askForm = event.target.closest("[data-ask-form]");
    const replyForm = event.target.closest("[data-reply-form]");
    const commentForm = event.target.closest("[data-comment-form]");
    const rejectForm = event.target.closest("[data-reject-form]");
    if (!askForm && !replyForm && !commentForm && !rejectForm) return;
    event.preventDefault();
    try {
      if (askForm) {
        const formData = new FormData(askForm);
        if (formData.get("topic_id") === "Other") formData.delete("topic_id");
        if (formData.get("version_id") === "Other") formData.delete("version_id");
        const data = await requestJson(config.createQuestionApi, { method: "POST", body: formData });
        showMessage(data.message || "Your question has been submitted and is under review");
        await refreshProducts();
        await loadQuestions();
      }
      if (replyForm) {
        const questionId = workspace.querySelector("[data-current-question]").dataset.currentQuestion;
        const data = await requestJson(`${config.detailApiBase}${questionId}${config.answerApiSuffix}`, { method: "POST", body: new FormData(replyForm) });
        renderDetail(data.question);
        showMessage("Reply added");
      }
      if (commentForm) {
        const questionId = workspace.querySelector("[data-current-question]").dataset.currentQuestion;
        await requestJson(`${config.answerCommentBase}${commentForm.dataset.commentForm}/comment`, { method: "POST", body: new FormData(commentForm) });
        await openQuestion(questionId);
        showMessage("Reply added");
      }
      if (rejectForm) {
        const questionId = rejectForm.dataset.rejectForm;
        await requestJson(`${config.approveBase}${questionId}/reject`, { method: "POST", body: new FormData(rejectForm) });
        showMessage("Question rejected.");
        await loadQuestions();
      }
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  renderTopicFilters();
  renderList();
  window.addEventListener("popstate", async () => {
    const id = new URLSearchParams(window.location.search).get("question_id");
    if (id) {
      await openQuestion(id);
    } else {
      await loadQuestions();
    }
  });
  const initialId = new URLSearchParams(window.location.search).get("question_id");
  if (initialId) openQuestion(initialId);
}
