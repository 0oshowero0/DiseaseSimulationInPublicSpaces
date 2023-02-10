export function exportToFile(content, filename, fileType) {
    if (!fileType) fileType = 'text/plain;charset=utf-8;';
    const blob = new Blob([content], {type: fileType});
    const url = URL.createObjectURL(blob);
    var a = window.document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
