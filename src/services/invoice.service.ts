import fs from "fs";
import path from "path";
import pdfParse from "pdf-parse";
import prisma from "../database/prisma";

export async function extractDataFromPDF(pdfPath: string) {
  try {
    const dataBuffer = fs.readFileSync(pdfPath);
    const data = await pdfParse(dataBuffer);
    const text = data.text;

    const clientNumberMatch = text.match(/Número do Cliente:\s*(\d+)/);
    const referenceMonthMatch = text.match(/Mês de Referência:\s*([A-Z]+\/\d{4})/);
    const energyConsumptionMatch = text.match(/Energia Elétrica\s+(\d+)\s+kWh/);
    const sceeeEnergyMatch = text.match(/Energia SCEEE s\/ICMS\s+(\d+)\s+kWh/);
    const compensatedEnergyMatch = text.match(/Energia Compensada GD I\s+(\d+)\s+kWh/);
    const publicLightingMatch = text.match(/Contrib Ilum Publica Municipal\s+R\$\s*([\d,.]+)/);

    const extractedData = {
      clientNumber: clientNumberMatch ? clientNumberMatch[1] : null,
      referenceMonth: referenceMonthMatch ? referenceMonthMatch[1] : null,
      energyConsumption: energyConsumptionMatch ? parseInt(energyConsumptionMatch[1]) : 0,
      sceeeEnergy: sceeeEnergyMatch ? parseInt(sceeeEnergyMatch[1]) : 0,
      compensatedEnergy: compensatedEnergyMatch ? parseInt(compensatedEnergyMatch[1]) : 0,
      publicLighting: publicLightingMatch ? parseFloat(publicLightingMatch[1].replace(",", ".")) : 0,
    };

    return extractedData;
  } catch (error) {
    console.error("Erro ao processar o PDF:", error);
    return null;
  }
}

export async function saveInvoiceData(pdfPath: string) {
  const data = await extractDataFromPDF(pdfPath);
  if (!data) return null;

  return prisma.invoice.create({ data });
}
