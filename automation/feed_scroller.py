# automation/feed_scroller.py (updated version)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import hashlib
import random

def scroll_slowly(driver, log_callback, max_posts):
    log_callback("Scrolling to load posts...", level="info")
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0
    scroll_attempts = 0
    
    while scroll_attempts < 15:
        posts = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-shared-update-v2')]")
        current_count = len(posts)
        log_callback(f"Found {current_count} posts so far...", level="debug")

        if current_count >= max_posts * 2:
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 2))  # Reduced delay

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
            log_callback(f"No new content loaded, attempt {scroll_attempts}/15", level="debug")
            if scroll_attempts >= 3:
                log_callback("No more new posts loading.", level="debug")
                break
        else:
            scroll_attempts = 0
            
        last_height = new_height
        attempts += 1
        if attempts > 20:
            log_callback("Max scroll attempts reached.", level="warn")
            break

    final_count = len(driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-shared-update-v2')]"))
    log_callback(f"Finished scrolling. Found {final_count} posts.", level="info")
    return final_count

def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
    time.sleep(random.uniform(0.5, 1))  # Reduced delay

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
        from ai.ai_generator import generate_text
        summary = generate_text(prompt)
        return summary.strip('"\'') if summary else "Summary not available."
    except Exception as e:
        return f"Error summarizing post: {e}"

def perform_action(driver, post, action, custom_comment, index, log_callback):
    try:
        scroll_to_element(driver, post)
        time.sleep(random.uniform(1, 2))  # Reduced delay
        
        if action == "like":
            try:
                like_button = post.find_element(By.XPATH, ".//button[contains(@class, 'social-actions-button') and contains(@aria-label, 'React Like')]")
                scroll_to_element(driver, like_button)
                like_button.click()
                log_callback(f"Liked post {index}", level="user")
                time.sleep(random.uniform(1, 2))  # Reduced delay
            except NoSuchElementException:
                log_callback(f"Like button not found for post {index}", level="debug")
                return False
                
        elif action == "comment":
            try:
                scroll_to_element(driver, post)
                time.sleep(random.uniform(1, 2))  # Reduced delay
                
                comment_button = post.find_element(By.XPATH, ".//button[contains(@class, 'social-actions-button') and contains(@class, 'comment-button')]")
                scroll_to_element(driver, comment_button)
                time.sleep(random.uniform(0.5, 1))  # Reduced delay
                comment_button.click()
                log_callback(f"Clicked comment button for post {index}", level="debug")
                
                time.sleep(random.uniform(1, 2))  # Reduced delay
                
                comment_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class, 'comments-comment-box')]//div[contains(@class, 'ql-editor') and @contenteditable='true']"))
                )
                
                comment_box.click()
                time.sleep(random.uniform(0.5, 1))  # Reduced delay
                
                comment_box.clear()
                comment_text = custom_comment or "Great post!"
                
                for char in comment_text:
                    comment_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.1))  # Reduced delay
                
                log_callback(f"Typed comment for post {index}: {comment_text}", level="debug")
                time.sleep(random.uniform(1, 2))  # Reduced delay
                
                try:
                    post_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class, 'comments-comment-box__submit-button') and not(@disabled)]"))
                    )
                    scroll_to_element(driver, post_button)
                    time.sleep(random.uniform(0.5, 1))  # Reduced delay
                    post_button.click()
                    log_callback(f"Clicked Post button for post {index}", level="user")
                except (NoSuchElementException, TimeoutException):
                    log_callback(f"Post button not found for post {index}, trying ENTER key", level="debug")
                    comment_box.send_keys(Keys.ENTER)
                    log_callback(f"Sent ENTER key for post {index}", level="debug")
                
                # Wait and check for LinkedIn error message
                time.sleep(random.uniform(2, 3))  # Reduced delay
                try:
                    error_message = driver.find_element(By.XPATH, "//*[contains(text(), 'comment could not be created') or contains(text(), 'error')]")
                    log_callback(f"LinkedIn error detected: {error_message.text}", level="user")
                    return False  # Fail gracefully, no retries
                except NoSuchElementException:
                    pass
                
                # Verify comment was actually posted
                time.sleep(random.uniform(2, 3))  # Reduced delay
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f".//span[contains(@class, 'comments-comment-item__comment-content') and contains(text(), '{comment_text}')]"))
                    )
                    log_callback(f"Comment verified on post {index}: {comment_text}", level="user")
                except TimeoutException:
                    log_callback(f"Comment not found on page for post {index}, assuming failure", level="user")
                    return False
                
                time.sleep(random.uniform(2, 3))  # Reduced delay
                log_callback(f"Commented on post {index}: {comment_text}", level="user")
                return True
            
            except (NoSuchElementException, TimeoutException) as e:
                log_callback(f"Failed to comment on post {index}: {str(e)}", level="user")
                return False
        
        return True
    except Exception as e:
        log_callback(f"Error performing action on post {index}: {str(e)}", level="user")
        return False

def process_post(driver, post, index, log_callback, get_action_callback):
    try:
        scroll_to_element(driver, post)
        time.sleep(random.uniform(1, 2))  # Reduced delay
        
        post_id = "unknown"
        post_content_hash = None

        try:
            post_id = driver.execute_script("return arguments[0].getAttribute('data-id');", post) or \
                      driver.execute_script("return arguments[0].getAttribute('data-urn');", post) or "unknown"
            log_callback(f"Post {index} ID (data-id/data-urn): {post_id}", level="debug")
        except Exception as e:
            log_callback(f"Error extracting data-id/data-urn for post {index}: {str(e)}", level="debug")

        if post_id == "unknown":
            try:
                post_link = post.find_element(
                    By.XPATH,
                    ".//a[contains(@class, 'app-aware-link') and contains(@href, '/feed/update/')]"
                )
                post_url = post_link.get_attribute("href").split('?')[0]
                post_id = post_url
                log_callback(f"Post {index} ID (URL): {post_id}", level="debug")
            except NoSuchElementException:
                log_callback(f"No post URL found for post {index}", level="debug")

        if post_id == "unknown":
            try:
                post_html = driver.execute_script("return arguments[0].outerHTML;", post)
                post_id = hashlib.md5(post_html.encode('utf-8')).hexdigest()
                log_callback(f"Post {index} ID (HTML hash fallback): {post_id[:10]}...", level="debug")
            except Exception as e:
                log_callback(f"Failed to extract HTML hash for post {index}: {str(e)}", level="error")

        author_name = "Unknown Author"
        try:
            author_element = post.find_element(
                By.XPATH,
                ".//span[contains(@class, 'update-components-actor__name')]//span[@dir='ltr']//span[@aria-hidden='true']"
            )
            author_name = author_element.text.strip()
            log_callback(f"Author of post {index}: {author_name}", level="debug")
        except NoSuchElementException:
            try:
                author_element = post.find_element(
                    By.XPATH,
                    ".//span[contains(@class, 'update-components-actor__title')]//span[@dir='ltr']//span[@aria-hidden='true']"
                )
                author_name = author_element.text.strip()
                log_callback(f"Author of post {index} (fallback 1): {author_name}", level="debug")
            except NoSuchElementException:
                try:
                    author_element = post.find_element(
                        By.XPATH,
                        ".//a[contains(@class, 'update-components-actor__meta')]//span"
                    )
                    author_name = author_element.text.strip()
                    log_callback(f"Author of post {index} (fallback 2): {author_name}", level="debug")
                except NoSuchElementException:
                    log_callback(f"Author name not found for post {index}", level="debug")

        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, ".//img[contains(@class, 'ivm-view-attr__img')]"))
            )
            log_callback(f"Images loaded for post {index}", level="debug")
        except TimeoutException:
            log_callback(f"No images found for post {index}", level="debug")

        post_text = "No text found"
        try:
            time.sleep(random.uniform(0.5, 1))  # Reduced delay
            
            post_text_elements = post.find_elements(
                By.XPATH,
                ".//div[contains(@class, 'update-components-text')]//span[@dir='ltr' and not(@aria-hidden='true')]"
            )
            
            if post_text_elements:
                raw_texts = []
                for elem in post_text_elements:
                    text = driver.execute_script("return arguments[0].textContent;", elem).strip()
                    if text and len(text) > 3:
                        raw_texts.append(text)
                
                if raw_texts:
                    post_text = " ".join([re.sub(r'\s+', ' ', text) for text in raw_texts if text.strip()])
                    log_callback(f"Extracted text for post {index}: {post_text[:100]}...", level="debug")
            
            if post_text == "No text found" or len(post_text) < 10:
                post_text_elements = post.find_elements(
                    By.XPATH,
                    ".//span[@dir='ltr' and not(@aria-hidden='true')]"
                )
                raw_texts = []
                for elem in post_text_elements:
                    text = driver.execute_script("return arguments[0].textContent;", elem).strip()
                    if text and len(text) > 3:
                        raw_texts.append(text)
                
                if raw_texts:
                    post_text = " ".join([re.sub(r'\s+', ' ', text) for text in raw_texts if text.strip()])
                    log_callback(f"Fallback text for post {index}: {post_text[:100]}...", level="debug")
                
        except Exception as e:
            log_callback(f"Error extracting text for post {index}: {str(e)}", level="debug")

        post_content_hash = hashlib.md5(post_text.encode('utf-8')).hexdigest()
        log_callback(f"Post {index} content hash: {post_content_hash}", level="debug")

        summary = summarize_post(post_text, index)
        log_callback(f"Summary for post {index}: {summary[:100]}...", level="user")

        action, custom_comment = get_action_callback(summary, index, author_name)
        log_callback(f"Selected action for post {index}: {action}", level="user")

        success = True
        if action != "skip":
            success = perform_action(driver, post, action, custom_comment, index, log_callback)

        return success, post_id, post_content_hash

    except Exception as e:
        log_callback(f"Error processing post {index}: {str(e)}", level="user")
        return False, None, None
    
def engage_feed(driver, max_posts=5, get_action_callback=None, log_callback=lambda msg, level: print(msg)):
    try:
        driver.get("https://www.linkedin.com/feed/") 
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-shared-update-v2')]"))
        )

        processed_posts = 0
        processed_post_ids = set()
        processed_content_hashes = set()

        # Initial scroll to load posts
        scroll_slowly(driver, log_callback, max_posts)

        while processed_posts < max_posts:
            post_containers = driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'feed-shared-update-v2') and .//div[contains(@class, 'update-components-text')]]"
            )
            
            log_callback(f"Found {len(post_containers)} total posts in feed", level="info")
            
            if not post_containers:
                log_callback("No posts found in feed", level="user")
                break

            # Process each post in the list
            found_new_post = False
            for idx, post in enumerate(post_containers):
                # Generate a unique identifier for this post
                try:
                    post_id = driver.execute_script("return arguments[0].getAttribute('data-id') || arguments[0].getAttribute('data-urn');", post)
                    if not post_id:
                        temp_content = driver.execute_script("return arguments[0].textContent;", post)[:100]
                        post_id = hashlib.md5((temp_content + str(idx)).encode('utf-8')).hexdigest()
                except:
                    post_id = f"post_{idx}_{processed_posts}"
                
                # Skip if we've already processed this post
                if post_id in processed_post_ids:
                    log_callback(f"Skipping already processed post at index {idx} (ID: {post_id})", level="debug")
                    continue

                # Process the post
                success, extracted_post_id, post_content_hash = process_post(
                    driver, post, processed_posts + 1, log_callback, get_action_callback
                )

                if not extracted_post_id or not post_content_hash:
                    log_callback(f"Skipping post at index {idx} due to processing error", level="debug")
                    continue

                # Check for duplicates using extracted IDs
                if extracted_post_id in processed_post_ids or post_content_hash in processed_content_hashes:
                    log_callback(f"Skipping duplicate post at index {idx} (ID: {extracted_post_id}, Hash: {post_content_hash})", level="debug")
                    continue
                
                processed_post_ids.add(extracted_post_id)
                processed_post_ids.add(post_id)  # Add both IDs to avoid reprocessing
                processed_content_hashes.add(post_content_hash)
                processed_posts += 1
                found_new_post = True
                
                log_callback(f"Processed {processed_posts}/{max_posts} posts", level="user")
                
                # Scroll to the next post or load more
                if idx + 1 < len(post_containers):
                    scroll_to_element(driver, post_containers[idx + 1])
                else:
                    log_callback("Reached end of loaded posts, scrolling to load more...", level="info")
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(1, 2))  # Reduced delay
                    scroll_slowly(driver, log_callback, max_posts - processed_posts)
                
                time.sleep(random.uniform(2, 3))  # Reduced delay between posts
                break  # Process one post at a time to ensure scrolling

            if not found_new_post:
                log_callback("No new posts found after scrolling, stopping...", level="user")
                break

        log_callback(f"Completed processing {processed_posts} posts", level="user")
        log_callback("✅ Feed interaction completed", level="user")

    except Exception as e:
        log_callback(f"Error in feed engagement: {str(e)}", level="user")