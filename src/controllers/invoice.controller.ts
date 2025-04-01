import { Request, Response } from "express";
import { saveInvoiceData } from "../services/invoice.service";
import path from "path";

export async function uploadInvoice(req: Request, res: Response) {
  if (!req.file) {
    return res.status(400).json({ error: "Arquivo PDF obrigatório" });
  }

  const pdfPath = path.join(__dirname, "../../faturas", req.file.filename);
  const invoice = await saveInvoiceData(pdfPath);

  return res.status(201).json(invoice);
}
