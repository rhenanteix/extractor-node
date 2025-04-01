import express from "express";
import multer from "multer";
import { uploadInvoice } from "../controllers/invoice.controller";

const router = express.Router();
const upload = multer({ dest: "faturas/" });

router.post("/upload", upload.single("file"), uploadInvoice);

export default router;
