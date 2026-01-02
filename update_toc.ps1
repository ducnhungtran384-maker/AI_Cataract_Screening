$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("C:\Users\weirui\Desktop\AI_Test\Final_Report_Temp.docx")
$doc.TablesOfContents.Item(1).Update()
$doc.Save()
$doc.Close()
$word.Quit()
