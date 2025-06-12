## To best scrape all the countries within the CIA World Factbook, you should go to https://www.cia.gov/the-world-factbook/countries/ and save the HTML as a file. See below.
  
  **Step 1:** Set the countires "Per Page" to **All**
<br> 
![image](https://github.com/user-attachments/assets/d78b7f87-ef2a-4356-85d6-cf1dacf44378)
<br>
<br>
   **Step 2:** Inspect the HTML. The container for all the countires should be within **\<div class="row">**. You can verify by locating the containers **\<div class="col-lg-12">**. These containers should have the titles and links for each country within.
<br>
![image](https://github.com/user-attachments/assets/0a891fb5-7404-44e8-b3c5-29cf16406d98)
<br>
<br>
   **Step 3:** Right-click the container for all the countires **\<div class="row">** and navigate to, then click **Copy Element**.
<br>
![image](https://github.com/user-attachments/assets/226cba95-5204-4bef-ab0b-be3465397be6)
<br>
<br>
  **Step 4:** Paste the copied HTML to a text editior of choice (i.e., Notepad). Save the document as a **".html"** into your workspace.
<br>
<br>
**This method works best as the CIA website can and will block sraping. Additionally, it is difficult to get around the countries "Per Page" obstacle because the default is set to 12 and cannot be easily adjusted programmatically.**

  
  
