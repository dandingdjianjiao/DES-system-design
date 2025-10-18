/**
 * Feedback Service - Handles experimental feedback submission API calls
 */

import api from './api';
import type { FeedbackRequest, FeedbackResponse } from '../types';

export const feedbackService = {
  /**
   * Submit experimental feedback for a recommendation
   * POST /api/v1/feedback
   */
  submitFeedback: async (
    feedbackData: FeedbackRequest
  ): Promise<FeedbackResponse> => {
    const response = await api.post<FeedbackResponse>(
      '/api/v1/feedback',
      feedbackData
    );
    return response.data;
  },
};
