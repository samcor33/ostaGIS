## To best scrape all the t_orgs within the CIA World Factbook, you should go to [CIA World Factbook - Terrorist Organizations](https://www.cia.gov/the-world-factbook/references/terrorist-organizations/) and save the HTML as a file. See below.
  
  **Step 1:** Set the countires "Per Page" to **All**
<br> 
![image](https://github.com/user-attachments/assets/801b408e-a179-4f32-aae2-6265ae70e910)
<br>
<br>
   **Step 2:** Inspect the HTML. The container for all the t_orgs should be within **\<div class="row">**. You can verify by locating the containers **\<div class="pb30">**. These containers should have the titles and all information for ther t_org within.
<br>
![image](https://github.com/user-attachments/assets/a3fb5307-492c-4b6b-8b59-ef9060d120cb)
<br>
<br>
   **Step 3:** Right-click the container for all the t_orgs **\<div class="row">** and navigate to, then click **Copy Element**.
<br>
![image](https://github.com/user-attachments/assets/226cba95-5204-4bef-ab0b-be3465397be6)
<br>
<br>
  **Step 4:** Paste the copied HTML to a text editior of choice (i.e., Notepad). Save the document as a **".html"** into your workspace.
<br>
<br>
**This method works best as the CIA website can and will block sraping. Additionally, it is difficult to get around the Terrorist Organizations "Per Page" obstacle because the default is set to 12 and cannot be easily adjusted programmatically.**
