import express from "express";
import cors from "cors";
import invoiceRoutes from "./routes/invoice.routes";

const app = express();
app.use(cors());
app.use(express.json());
app.use("/api/invoices", invoiceRoutes);

export default app;
