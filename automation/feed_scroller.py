from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import tkinter as tk
from tkinter import ttk, messagebox
from ai.ai_generator import generate_text
from PIL import Image, ImageTk
import re

def scroll_slowly(driver, log_callback, max_posts):
    log_callback("Scrolling to load posts...", level="info")
    body = driver.find_element(By.TAG_NAME, "body")
    post_count = 0
    max_attempts = 10
    attempt = 0
    
    while post_count < max_posts and attempt < max_attempts:
        posts = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-shared-update-v2') and .//div[contains(@class, 'update-components-text')]]")
        post_count = len(posts)
        log_callback(f"Found {post_count} posts so far...", level="debug")
        
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(3)
        attempt += 1
    
    log_callback(f"Finished scrolling. Found {post_count} posts.", level="info")
    return post_count

def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
    time.sleep(1)

def summarize_post(post_text, post_index):
    if not post_text or post_text.strip() == "No text found":
        return "There is no LinkedIn post provided to summarize. The provided text indicates no content was found. Therefore, no summary can be created."
    
    prompt = f"""
    Summarize the following LinkedIn post (Post {post_index} at {time.time()}) in 2-3 sentences (max 100 words):
    '{post_text}'
    
    Rules:
    1. Capture the main idea and key points.
    2. Keep it concise, clear, and professional.
    3. Avoid adding external information or opinions.
    """
    try:
        summary = generate_text(prompt)
        return summary.strip('"\'') if summary else "Summary not available."
    except Exception as e:
        return f"Error summarizing post: {e}"

def get_action_input(root, summary, post_index):
    dialog = tk.Toplevel(root)
    dialog.title(f"Post {post_index} Action")
    dialog.geometry("500x400")
    dialog.resizable(False, False)
    
    logo_path = "assets/logo.png"  # Replace with your logo path
    try:
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        dialog.iconphoto(True, logo_photo)
    except Exception as e:
        print(f"Error loading logo: {e}")
    
    frame = ttk.Frame(dialog, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text=f"Post {post_index} Summary:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
    summary_text = tk.Text(frame, height=6, width=50, wrap=tk.WORD, state=tk.NORMAL)
    summary_text.insert(tk.END, summary)
    summary_text.config(state=tk.DISABLED)
    summary_text.pack(fill=tk.X, pady=5)
    
    ttk.Label(frame, text="Action:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
    action_var = tk.StringVar(value="skip")
    action_frame = ttk.Frame(frame)
    action_frame.pack(fill=tk.X, pady=5)
    
    ttk.Radiobutton(action_frame, text="Like", value="like", variable=action_var).pack(side=tk.LEFT, padx=10)
    ttk.Radiobutton(action_frame, text="Comment", value="comment", variable=action_var).pack(side=tk.LEFT, padx=10)
    ttk.Radiobutton(action_frame, text="Skip", value="skip", variable=action_var).pack(side=tk.LEFT, padx=10)
    
    comment_frame = ttk.Frame(frame)
    comment_frame.pack(fill=tk.X, pady=5)
    ttk.Label(comment_frame, text="Comment (if selected):").pack(anchor=tk.W)
    comment_text = tk.Text(comment_frame, height=3, width=50)
    comment_text.pack(fill=tk.X, pady=5)
    
    result = {"action": None, "comment": None}
    
    def submit():
        result["action"] = action_var.get()
        if result["action"] == "comment":
            result["comment"] = comment_text.get("1.0", tk.END).strip()
        dialog.destroy()
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    ttk.Button(button_frame, text="Submit", command=submit).pack(side=tk.RIGHT)
    
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    
    return result["action"], result["comment"]

def process_post(driver, post, index, root, log_callback):
    try:
        scroll_to_element(driver, post)
        
        post_id = driver.execute_script("return arguments[0].getAttribute('data-id');", post) or "unknown"
        log_callback(f"Processing post {index} with data-id: {post_id}", level="debug")
        
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//img[contains(@class, 'ivm-view-attr__img')]"))
            )
            log_callback(f"Images loaded for post {index}", level="debug")
        except TimeoutException:
            log_callback(f"No images found or failed to load for post {index}", level="debug")
        
        post_text = "No text found"
        try:
            post_text_elements = post.find_elements(By.XPATH, ".//div[contains(@class, 'update-components-text')]//span[@dir='ltr' and not(@aria-hidden='true')]")
            if post_text_elements:
                raw_texts = []
                for elem in post_text_elements:
                    raw_html = driver.execute_script("return arguments[0].innerHTML;", elem)
                    log_callback(f"Primary HTML for post {index}: {raw_html[:200]}...", level="debug")
                    text = driver.execute_script("return arguments[0].textContent;", elem).strip()
                    if text:
                        raw_texts.append(text)
                post_text = " ".join([re.sub(r'\s+', ' ', text) for text in raw_texts if text.strip()]) or "No text found"
                log_callback(f"Primary text for post {index}: {post_text[:100]}...", level="debug")
            
            if post_text == "No text found":
                post_text_elements = post.find_elements(By.XPATH, ".//span[@dir='ltr' and not(@aria-hidden='true')]")
                raw_texts = []
                for elem in post_text_elements:
                    raw_html = driver.execute_script("return arguments[0].innerHTML;", elem)
                    log_callback(f"Fallback HTML for post {index}: {raw_html[:200]}...", level="debug")
                    text = driver.execute_script("return arguments[0].textContent;", elem).strip()
                    if text:
                        raw_texts.append(text)
                post_text = " ".join([re.sub(r'\s+', ' ', text) for text in raw_texts if text.strip()]) or "No text found"
                log_callback(f"Fallback text for post {index}: {post_text[:100]}...", level="debug")
            
            if post_text == "No text found":
                full_html = driver.execute_script("return arguments[0].outerHTML;", post)
                log_callback(f"Full post HTML for post {index}: {full_html[:500]}...", level="debug")
        except Exception as e:
            log_callback(f"Error extracting text for post {index}: {str(e)}", level="debug")
        
        summary = summarize_post(post_text, index)
        log_callback(f"Summary: {summary}", level="user")
        
        action, custom_comment = get_action_input(root, summary, index)
        log_callback(f"Selected action for post {index}: {action}", level="user")
        
        if action == "like":
            try:
                like_button = post.find_element(By.XPATH, ".//button[contains(@class, 'social-actions-button') and contains(@aria-label, 'React Like')]")
                scroll_to_element(driver, like_button)
                like_button.click()
                log_callback(f"Liked post {index}", level="user")
            except NoSuchElementException:
                button_html = driver.execute_script("return arguments[0].outerHTML;", post)
                log_callback(f"Like button not found for post {index}. Post HTML: {button_html[:500]}...", level="debug")
                return False
        elif action == "comment":
            try:
                comment_button = post.find_element(By.XPATH, ".//button[contains(@class, 'social-actions-button') and contains(@class, 'comment-button')]")
                scroll_to_element(driver, comment_button)
                comment_button.click()
                log_callback(f"Clicked comment button for post {index}", level="debug")
                
                comment_box = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class, 'comments-comment-box')]//div[contains(@class, 'ql-editor') and @contenteditable='true']"))
                )
                comment_box.click()
                comment_box.send_keys(custom_comment or "Great post!")
                log_callback(f"Typed comment for post {index}: {custom_comment or 'Great post!'}", level="debug")
                
                try:
                    post_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class, 'comments-comment-box__submit-button')]"))
                    )
                    scroll_to_element(driver, post_button)
                    post_button.click()
                    log_callback(f"Clicked Post button for post {index}", level="user")
                except (NoSuchElementException, TimeoutException):
                    log_callback(f"Post button not found for post {index}, trying ENTER key", level="debug")
                    comment_box.send_keys(Keys.ENTER)
                    log_callback(f"Sent ENTER key for post {index}", level="debug")
                
                time.sleep(2)
                log_callback(f"Commented on post {index}: {custom_comment or 'Great post!'}", level="user")
            except (NoSuchElementException, TimeoutException) as e:
                log_callback(f"Failed to comment on post {index}: {str(e)}", level="user")
                return False
        
        return True
    except Exception as e:
        log_callback(f"Error processing post {index}: {str(e)}", level="user")
        return False

def engage_feed(driver, max_posts=5, root=None, log_callback=lambda msg, level: print(msg)):
    try:
        driver.get("https://www.linkedin.com/feed/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-shared-update-v2')]"))
        )
        
        processed_posts = 0
        while processed_posts < max_posts:
            post_count = scroll_slowly(driver, log_callback, max_posts)
            if post_count == 0:
                log_callback("No posts found in feed", level="user")
                return
            
            post_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-shared-update-v2') and .//div[contains(@class, 'update-components-text')]]")
            log_callback(f"Found {len(post_containers)} posts to process", level="info")
            
            for index, post in enumerate(post_containers, processed_posts + 1):
                if processed_posts >= max_posts:
                    log_callback(f"Reached max posts limit ({max_posts})", level="user")
                    break
                log_callback(f"Processing post {index}...", level="user")
                success = process_post(driver, post, index, root, log_callback)
                if success:
                    processed_posts += 1
                else:
                    log_callback(f"Skipping post {index} due to processing error", level="user")
                time.sleep(2)
            
            if processed_posts < max_posts:
                log_callback("Refreshing post list for more content...", level="info")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
        
        log_callback(f"Processed {processed_posts} posts", level="user")
        log_callback("✅ Feed interaction completed", level="user")
    except Exception as e:
        log_callback(f"Error in feed engagement: {str(e)}", level="user")