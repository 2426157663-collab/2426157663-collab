Add-Type -AssemblyName System.Drawing

$source = @"
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

public static class GprRenderer
{
    public static void Render(string input, string output)
    {
        byte[] data = File.ReadAllBytes(input);
        int samples = BitConverter.ToUInt16(data, 3220);
        int traceSize = 240 + samples * 2;
        int traces = (data.Length - 3600) / traceSize;

        List<int> levels = new List<int>();
        for (int t = 0; t < traces; t += 20)
        {
            int traceOffset = 3600 + t * traceSize + 240;
            for (int s = 0; s < samples; s += 4)
            {
                levels.Add(Math.Abs((int)BitConverter.ToInt16(data, traceOffset + s * 2)));
            }
        }
        levels.Sort();
        int clip = Math.Max(1, levels[(int)(levels.Count * 0.985)]);

        int width = 1800, height = 820;
        int left = 125, top = 70, plotWidth = 1600, plotHeight = 650;
        using (Bitmap image = new Bitmap(width, height, PixelFormat.Format24bppRgb))
        using (Graphics g = Graphics.FromImage(image))
        {
            g.Clear(Color.White);
            for (int x = 0; x < plotWidth; x++)
            {
                int trace = x * (traces - 1) / (plotWidth - 1);
                int traceOffset = 3600 + trace * traceSize + 240;
                for (int y = 0; y < plotHeight; y++)
                {
                    int sample = y * (samples - 1) / (plotHeight - 1);
                    int value = BitConverter.ToInt16(data, traceOffset + sample * 2);
                    int gray = 128 + value * 127 / clip;
                    if (gray < 0) gray = 0;
                    if (gray > 255) gray = 255;
                    image.SetPixel(left + x, top + y, Color.FromArgb(gray, gray, gray));
                }
            }

            using (Pen axis = new Pen(Color.Black, 2))
            using (Pen grid = new Pen(Color.FromArgb(90, 255, 255, 255), 1))
            using (Font tick = new Font("Microsoft YaHei", 14))
            using (Brush text = new SolidBrush(Color.Black))
            {
                g.DrawRectangle(axis, left, top, plotWidth, plotHeight);
                for (int i = 0; i <= 5; i++)
                {
                    int x = left + i * plotWidth / 5;
                    int traceNo = 1 + i * (traces - 1) / 5;
                    g.DrawLine(grid, x, top, x, top + plotHeight);
                    g.DrawString(traceNo.ToString(), tick, text, x - 28, top + plotHeight + 8);

                    int y = top + i * plotHeight / 5;
                    double timeNs = i * samples * 0.390 / 5.0;
                    g.DrawLine(grid, left, y, left + plotWidth, y);
                    g.DrawString(timeNs.ToString("0"), tick, text, 65, y - 10);
                }
                g.DrawString("ns", tick, text, 74, 28);
            }
            image.Save(output, ImageFormat.Png);
        }
    }
}
"@

Add-Type -TypeDefinition $source -ReferencedAssemblies System.Drawing
[GprRenderer]::Render("C:\lab\prism2\DAT_0002_REVERSED.SGY", "C:\lab\prism2\DAT_0002_REVERSED_VM.png")
