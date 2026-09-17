import { NextRequest, NextResponse } from "next/server";
import { lookupLemma } from "@/lib/lexicon";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ lemma: string }> }
) {
  const { lemma: encoded } = await params;
  const lemma = decodeURIComponent(encoded);
  const result = lookupLemma(lemma);
  return NextResponse.json(result);
}
