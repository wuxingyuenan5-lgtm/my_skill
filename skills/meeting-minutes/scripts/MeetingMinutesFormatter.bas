Attribute VB_Name = "MeetingMinutesFormatter"
'=============================================================
'  MeetingMinutesFormatter.bas
'  会议纪要一键排版宏 v2.0
'  配合 meeting-minutes-skill.md 使用
'  使用方式：Word → 开发工具 → Visual Basic → 导入此 .bas
'            或直接复制粘贴到 Normal 模板的模块中
'=============================================================

Option Explicit

'--- 颜色常量 ---
Private Const COLOR_DARK_BLUE   As Long = 4207104   ' RGB(0,32,96)  深蓝
Private Const COLOR_BLUE_LINE   As Long = 14866960   ' RGB(0,112,192) 蓝色竖线
Private Const COLOR_ORANGE      As Long = 26367      ' RGB(192,80,0)  橙色
Private Const COLOR_LIGHT_GRAY  As Long = 15790320   ' RGB(242,242,242) 浅灰
Private Const COLOR_GRAY_TEXT   As Long = 8421504    ' RGB(128,128,128) 灰色
Private Const COLOR_DARK_GRAY   As Long = 4210752    ' RGB(64,64,64)  深灰

'--- 字体常量 ---
Private Const FONT_BODY        As String = "微软雅黑"

'=============================================================
'  主入口：一键排版
'=============================================================
Public Sub FormatMeetingMinutes()

    Dim para As Paragraph
    Dim styleName As String
    Dim doc As Document
    Set doc = ActiveDocument

    '--- 关闭屏幕刷新，加速 ---
    Application.ScreenUpdating = False

    '--- 第一步：清理多余空行 ---
    Call RemoveExtraBlankLines(doc)

    '--- 第二步：遍历每个段落，识别标记并套用样式 ---
    Dim i As Long
    i = 1
    Do While i <= doc.Paragraphs.Count
        Set para = doc.Paragraphs(i)

        If para.Range.Text = Chr(13) & Chr(13) Then GoTo NextPara

        ' 识别标题层级
        If Left$(Trim$(para.Range.Text), 2) = "# " Then
            Call ApplyH1(para)
            para.Range.Text = Mid$(Trim$(para.Range.Text), 3)
            Call ApplyH1(para)

        ElseIf Left$(Trim$(para.Range.Text), 3) = "## " Then
            Call ApplyH2(para)
            para.Range.Text = Mid$(Trim$(para.Range.Text), 4)

        ElseIf Left$(Trim$(para.Range.Text), 4) = "### " Then
            Call ApplyH3(para)
            para.Range.Text = Mid$(Trim$(para.Range.Text), 5)

        ElseIf Left$(Trim$(para.Range.Text), 2) = "- " Then
            Call ApplyBulletItem(para)

        ElseIf Left$(Trim$(para.Range.Text), 2) = "Q：" Or _
               Left$(Trim$(para.Range.Text), 2) = "Q：" Then
            Call ApplyQA(para)

        ElseIf para.Range.Tables.Count > 0 Then
            Call FormatTable(para.Range.Tables(1))

        Else
            Call ApplyBodyText(para)
        End If

        '--- 处理加粗橙色高亮 ---
        Call HighlightOrangeBold(para)

NextPara:
        i = i + 1
    Loop

    '--- 第三步：全局美化 ---
    Call SetPageMargins(doc)
    Call AddSpaceAfterHeadings(doc)

    Application.ScreenUpdating = True
    MsgBox "✅ 会议纪要排版完成！", vbInformation, "MeetingMinutesFormatter"

End Sub

'=============================================================
'  样式应用子程序
'=============================================================

'--- H1：大标题 深蓝 18pt 加粗 居中 ---
Private Sub ApplyH1(p As Paragraph)
    With p.Range.Font
        .Name = FONT_BODY
        .Size = 18
        .Bold = True
        .Color = COLOR_DARK_BLUE
    End With
    p.Alignment = wdAlignParagraphCenter
    p.SpaceBefore = 0
    p.SpaceAfter = 16
End Sub

'--- H2：节标题 深蓝 14pt 加粗 带蓝色竖线 ---
Private Sub ApplyH2(p As Paragraph)
    Dim rng As Range
    Set rng = p.Range

    ' 在开头插入蓝色竖线字符
    rng.InsertBefore "▌ "
    rng.Characters(1).Font.Color = COLOR_BLUE_LINE
    rng.Characters(1).Font.Size = 14
    rng.Characters(1).Font.Bold = True

    With rng.Font
        .Name = FONT_BODY
        .Size = 14
        .Bold = True
        .Color = COLOR_DARK_BLUE
    End With
    p.Alignment = wdAlignParagraphLeft
    p.SpaceBefore = 18
    p.SpaceAfter = 10
End Sub

'--- H3：子标题 深灰 12pt 加粗 ---
Private Sub ApplyH3(p As Paragraph)
    With p.Range.Font
        .Name = FONT_BODY
        .Size = 12
        .Bold = True
        .Color = COLOR_DARK_GRAY
    End With
    p.SpaceBefore = 12
    p.SpaceAfter = 6
End Sub

'--- 正文 11pt 黑色 ---
Private Sub ApplyBodyText(p As Paragraph)
    With p.Range.Font
        .Name = FONT_BODY
        .Size = 11
        .Bold = False
        .Color = wdColorBlack
    End With
    p.SpaceBefore = 2
    p.SpaceAfter = 6
    p.LineSpacing = 1.5
End Sub

'--- 项目符号列表 ---
Private Sub ApplyBulletItem(p As Paragraph)
    p.Range.Text = Mid$(Trim$(p.Range.Text), 3) & Chr(13)
    With p.Range.Font
        .Name = FONT_BODY
        .Size = 11
        .Color = wdColorBlack
    End With
    p.Range.ListFormat.ApplyBulletDefault
    p.SpaceBefore = 2
    p.SpaceAfter = 2
End Sub

'--- Q&A 段落 浅灰底纹 ---
Private Sub ApplyQA(p As Paragraph)
    With p.Range.Font
        .Name = FONT_BODY
        .Size = 11
        .Color = wdColorBlack
    End With
    p.Range.Shading.BackgroundPatternColor = COLOR_LIGHT_GRAY
    p.SpaceBefore = 4
    p.SpaceAfter = 4
    p.LeftIndent = 18
End Sub

'=============================================================
'  表格美化
'=============================================================
Private Sub FormatTable(tbl As Table)
    Dim row As row, cell As Cell
    Dim r As Long

    ' 表头行
    With tbl.Rows(1).Range
        .Font.Name = FONT_BODY
        .Font.Size = 10.5
        .Font.Bold = True
        .Font.Color = wdColorWhite
        .Shading.BackgroundPatternColor = COLOR_DARK_BLUE
        .ParagraphFormat.Alignment = wdAlignParagraphCenter
    End With

    ' 数据行 斑马纹
    For r = 2 To tbl.Rows.Count
        Set row = tbl.Rows(r)
        With row.Range
            .Font.Name = FONT_BODY
            .Font.Size = 10.5
            .Font.Color = wdColorBlack
            .ParagraphFormat.Alignment = wdAlignParagraphCenter
        End With
        If r Mod 2 = 0 Then
            row.Range.Shading.BackgroundPatternColor = COLOR_LIGHT_GRAY
        Else
            row.Range.Shading.BackgroundPatternColor = wdColorWhite
        End If
    Next r

    ' 边框
    tbl.Borders.Enable = True
    tbl.Borders.OutsideLineWidth = wdLineWidth050pt
    tbl.Borders.InsideLineWidth = wdLineWidth050pt
    tbl.Borders.Color = COLOR_GRAY_TEXT

    ' 自动适配列宽
    tbl.AutoFitBehavior wdAutoFitContent
End Sub

'=============================================================
'  橙色加粗高亮：将 **text** 格式的文本设为橙色加粗
'=============================================================
Private Sub HighlightOrangeBold(p As Paragraph)
    Dim rng As Range
    Set rng = p.Range
    Dim startPos As Long, endPos As Long
    Dim searchText As String
    searchText = rng.Text

    ' 查找 ** 包裹的内容
    Dim i As Long
    i = 1
    Do
        startPos = InStr(i, searchText, "**", vbBinaryCompare)
        If startPos = 0 Then Exit Do
        endPos = InStr(startPos + 2, searchText, "**", vbBinaryCompare)
        If endPos = 0 Then Exit Do

        ' 删除 ** 标记并设橙色加粗
        Dim boldRng As Range
        Set boldRng = rng.Duplicate
        boldRng.Start = rng.Start + startPos - 1
        boldRng.End = rng.Start + endPos + 1

        ' 去掉 **
        boldRng.Text = Mid$(searchText, startPos + 2, endPos - startPos - 2)
        boldRng.Font.Color = COLOR_ORANGE
        boldRng.Font.Bold = True

        ' 更新搜索位置
        searchText = rng.Text
        i = startPos
    Loop
End Sub

'=============================================================
'  清理多余空行
'=============================================================
Private Sub RemoveExtraBlankLines(doc As Document)
    Dim find As Find
    Set find = doc.Content.Find
    With find
        .ClearFormatting
        .Text = "[^13]{2,}"
        .Replacement.Text = Chr(13) & Chr(13)
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchWildcards = True
        .Execute Replace:=wdReplaceAll
    End With
End Sub

'=============================================================
'  页面边距设置
'=============================================================
Private Sub SetPageMargins(doc As Document)
    With doc.PageSetup
        .TopMargin = CentimetersToPoints(2.54)
        .BottomMargin = CentimetersToPoints(2.54)
        .LeftMargin = CentimetersToPoints(3.17)
        .RightMargin = CentimetersToPoints(3.17)
    End With
End Sub

'=============================================================
'  标题后增加间距
'=============================================================
Private Sub AddSpaceAfterHeadings(doc As Document)
    Dim para As Paragraph
    For Each para In doc.Paragraphs
        If para.Range.Font.Size >= 14 And para.Range.Font.Bold Then
            para.SpaceAfter = 12
        End If
    Next para
End Sub

'=============================================================
'  辅助：快速选中整篇文档
'=============================================================
Private Sub SelectAll(doc As Document)
    doc.Content.Select
End Sub
